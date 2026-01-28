const { default: makeWASocket, DisconnectReason, useMultiFileAuthState } = require('@whiskeysockets/baileys')
const qrcode = require('qrcode-terminal')
const { execSync } = require('child_process')
const path = require('path')
const projectRoot = path.resolve(__dirname, '..')
const fs = require('fs')

async function startBot() {
  const { state, saveCreds } = await useMultiFileAuthState('auth_info')

  const sock = makeWASocket({
    auth: state,
  })

  sock.ev.on('creds.update', saveCreds)

  sock.ev.on('connection.update', (update) => {
    const { connection, lastDisconnect, qr } = update

    if (qr) {
      console.log('📱 Scan this QR with WhatsApp → Linked Devices:')
      qrcode.generate(qr, { small: true })
    }

    if (connection === 'close') {
      const shouldReconnect =
        lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut
      console.log('Connection closed, reconnecting?', shouldReconnect)
      if (shouldReconnect) startBot()
    } else if (connection === 'open') {
      console.log('✅ Bot connected & ready for /gate /repair!')
    }
  })

  sock.ev.on('messages.upsert', async ({ messages }) => {
    try {
      const msg = messages[0]
      console.log('messages.upsert received:', JSON.stringify(msg && { key: msg.key, messageType: Object.keys(msg.message || {})[0], messagePreview: (msg.message?.conversation || msg.message?.extendedTextMessage?.text || msg.message?.imageMessage?.caption || '').slice(0,200) }, null, 2))
      if (!msg || !msg.message) return

      // allow linked-device (lid) messages: these can have `fromMe: true` but include `remoteJidAlt`
      const isFromMe = !!msg.key?.fromMe;
      const isLinkedDevice = !!msg.key?.remoteJidAlt || msg.key?.addressingMode === 'lid';
      if (isFromMe && !isLinkedDevice) return;

      const sender = msg.key.remoteJidAlt || msg.key.remoteJid
      const text = msg.message.conversation || msg.message.extendedTextMessage?.text || msg.message?.imageMessage?.caption || ''

      // normalize '/gate/submissions/...' to '/gate submissions/...'
      const normalized = text.replace(/^\/gate\//, '/gate ').trim()

      if (normalized.startsWith('/gate')) {
        // immediate acknowledgement
        await sock.sendMessage(sender, { text: '🛡️ gatekeeper response' }, { quoted: msg })

        // run gatekeeper and return output
        const file = normalized.replace('/gate', '').replace(/^\//, '').trim() || 'submissions/broken.py'
        try {
          let cmd
          // use local validate.py script (standalone validator, no API)
          const validateScript = path.join(projectRoot, 'validate.py')
          cmd = `python3 ${validateScript} "${file}"`

          const result = execSync(cmd, { encoding: 'utf8', cwd: projectRoot })
          await sock.sendMessage(sender, { text: `🛡️ ${result}` }, { quoted: msg })
        } catch (e) {
          const hint = 'Install the gatekeeper package in the bot environment or provide a local gatekeeper.py'
          await sock.sendMessage(sender, { text: `❌ ${e.message}\n${hint}` }, { quoted: msg })
        }
      }

      if (text === '/repair') {
        try {
          const result = execSync(`python3 repair_loop_v3.py`, { encoding: 'utf8', cwd: projectRoot })
          await sock.sendMessage(sender, { text: `🔧 ${result}` }, { quoted: msg })
        } catch (e) {
          await sock.sendMessage(sender, { text: `❌ ${e.message}` }, { quoted: msg })
        }
      }
    } catch (err) {
      console.error('messages.upsert handler error', err)
    }
  })
}

startBot()
