#!/usr/bin/env bash
set -euo pipefail

OUTPUT_FILE="$1"

if [[ ! -f "$OUTPUT_FILE" ]]; then
  echo "No output file found"
  exit 0
fi

COMMENT_BODY="$(cat "$OUTPUT_FILE")"

# Add a stable header so we can find/replace the comment
HEADER="<!-- gatekeeper-comment -->"
BODY="$HEADER"$'\n\n'"$COMMENT_BODY"

# Install gh if needed
if ! command -v gh >/dev/null 2>&1; then
  echo "Installing gh CLI..."
  sudo apt-get update -y
  sudo apt-get install -y gh
fi

# Authenticate
echo "$GITHUB_TOKEN" | gh auth login --with-token

# Find existing Gatekeeper comment (if any)
COMMENT_ID="$(gh api repos/$GITHUB_REPOSITORY/issues/$GITHUB_PULL_NUMBER/comments \
  --jq '.[] | select(.body | contains("gatekeeper-comment")) | .id' || true)"

if [[ -n "$COMMENT_ID" ]]; then
  echo "Updating existing Gatekeeper comment"
  gh api repos/$GITHUB_REPOSITORY/issues/comments/$COMMENT_ID \
    -X PATCH -f body="$BODY"
else
  echo "Creating new Gatekeeper comment"
  gh api repos/$GITHUB_REPOSITORY/issues/$GITHUB_PULL_NUMBER/comments \
    -f body="$BODY"
fi
