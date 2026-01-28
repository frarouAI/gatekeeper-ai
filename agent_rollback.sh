#!/usr/bin/env bash
set -euo pipefail

LATEST=$(ls -dt .agent_backups/* 2>/dev/null | head -n1)

if [ -z "$LATEST" ]; then
  echo "❌ No backups available."
  exit 1
fi

echo "⏪ Restoring from $LATEST"
rsync -a --delete "$LATEST/" ./

echo "✅ Rollback complete."
