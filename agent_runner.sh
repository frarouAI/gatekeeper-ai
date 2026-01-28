#!/usr/bin/env bash
set -euo pipefail

TASK_FILE="CLAWDBOT_TASK.txt"
PATCH_FILE="CLAWDBOT_PATCH.diff"
BACKUP_DIR=".agent_backups/$(date +%Y%m%d_%H%M%S)"

echo "🤖 Clawdbot Local Agent Runner"
echo "-------------------------------"

if [ ! -f "$TASK_FILE" ]; then
  echo "❌ Missing $TASK_FILE"
  exit 1
fi

mkdir -p .agent_backups
echo "📦 Backing up repo to $BACKUP_DIR"
rsync -a --exclude '.agent_backups' ./ "$BACKUP_DIR/" >/dev/null

echo "📨 Task loaded from $TASK_FILE"
echo ""
echo "👉 Paste contents of $TASK_FILE into Clawdbot now."
echo "👉 Paste unified diffs into $PATCH_FILE"
echo ""
read -p "Press ENTER once diffs are pasted into $PATCH_FILE..."

if [ ! -s "$PATCH_FILE" ]; then
  echo "❌ $PATCH_FILE is empty."
  exit 1
fi

echo "🧩 Applying patch..."
git apply --reject --whitespace=fix "$PATCH_FILE" || {
  echo "❌ Patch failed to apply."
  echo "💡 Restore with: ./agent_rollback.sh"
  exit 1
}

echo "✅ Patch applied."

echo ""
echo "🔍 Running strict gate..."
python3 claude_cli.py . --gate --profile strict || {
  echo "❌ Gate failed."
  echo "💡 Restore with: ./agent_rollback.sh"
  exit 1
}

echo ""
echo "🧪 Running single-file test..."
python3 claude_cli.py judge submissions/example.py || {
  echo "❌ Judge test failed."
  echo "💡 Restore with: ./agent_rollback.sh"
  exit 1
}

echo ""
echo "🟢 Agent step SUCCESSFUL."
echo "You may now generate the next instruction set."
