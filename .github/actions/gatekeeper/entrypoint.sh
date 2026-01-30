#!/usr/bin/env bash
set -euo pipefail

PATH_TO_SCAN="${1:-.}"

~/.local/bin/gatekeeper "$PATH_TO_SCAN"
