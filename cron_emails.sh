#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/venv/bin/activate"
SUMMARY=$(python "$DIR/summarize_emails.py" 2>&1)
python "$DIR/send.py" "$SUMMARY"
