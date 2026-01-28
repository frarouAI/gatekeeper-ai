#!/usr/bin/env python3
"""
WhatsApp Code Judge Bot via Twilio
Send code → Get instant review
"""
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from bot_server import CodeJudgeBot, CONFIG
import os

app = Flask(__name__)

# Twilio credentials (get from https://console.twilio.com)
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', 'your_account_sid')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', 'your_auth_token')
TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

bot = CodeJudgeBot(CONFIG)
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Store conversation state
user_states = {}


@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages"""
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    
    resp = MessagingResponse()
    msg = resp.message()
    
    # Check if it's code (starts with def, import, class, etc.)
    if any(incoming_msg.startswith(keyword) for keyword in ['def ', 'import ', 'class ', 'from ', '@']):
        # Judge the code
        try:
            result = bot.judge_code(incoming_msg, from_number)
            verdict = bot.format_verdict(result)
            msg.body(verdict)
        except Exception as e:
            msg.body(f"❌ Error judging code: {str(e)}")
    
    elif incoming_msg.lower() in ['help', 'hi', 'hello', 'start']:
        msg.body("""
🤖 *Code Judge Bot*

Send me Python code and I'll review it!

*Features:*
✅ Correctness check
✅ Security scan
✅ Performance analysis
✅ Style review
✅ Code execution test

*Example:*
```
import math

def area(r):
    return math.pi * r ** 2
```

Try it now!
        """)
    
    else:
        msg.body("📝 Send me Python code to review, or type 'help' for instructions.")
    
    return str(resp)


@app.route('/status', methods=['GET'])
def status():
    """Health check endpoint"""
    return {"status": "running", "bot": "Code Judge WhatsApp"}


if __name__ == '__main__':
    print("🚀 WhatsApp Bot starting on http://localhost:5000")
    print("📱 Configure Twilio webhook: http://your-server:5000/webhook")
    app.run(host='0.0.0.0', port=5000, debug=True)
