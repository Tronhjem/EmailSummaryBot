#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
export PATH="/usr/local/bin:$PATH"
set -a; source "$DIR/.env"; set +a
SUMMARY=$(python3 "$DIR/summarize_emails.py" 2>&1)
python3 "$DIR/send.py" "$SUMMARY"
