#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
export PATH="/usr/local/bin:$PATH"
source "$DIR/venv/bin/activate"
set -a; source "$DIR/.env"; set +a
SUMMARY=$(python "$DIR/summarize_emails.py" 2>&1)
python "$DIR/send.py" "$SUMMARY"
