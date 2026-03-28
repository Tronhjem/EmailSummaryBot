"""Fetch unread Gmail messages and summarize them using the Claude API."""

import argparse
import os
import re
from pathlib import Path

import anthropic
from dotenv import load_dotenv

import gmail

load_dotenv()

PROMPT_PATH = Path(__file__).parent / "prompts" / "email_summary.md"
MAX_BODY_CHARS = 600
MODEL = "claude-haiku-4-5-20251001"


def format_emails_for_prompt(messages):
    """Format email dicts into a text block for the Claude prompt."""
    if not messages:
        return "No unread emails."

    parts = []
    for i, msg in enumerate(messages, 1):
        body = msg["body"][:MAX_BODY_CHARS]
        if len(msg["body"]) > MAX_BODY_CHARS:
            body += "... (truncated)"
        parts.append(
            f"--- Email {i} ---\n"
            f"From: {msg['from']}\n"
            f"Subject: {msg['subject']}\n"
            f"Date: {msg['date']}\n"
            f"Body:\n{body}"
        )
    return "\n\n".join(parts)


def call_claude(prompt, content):
    """Call the Claude API and return the response."""
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        temperature=0,
        system=prompt,
        messages=[
            {"role": "user", "content": f"Here are the emails:\n\n{content}"}
        ],
    )
    return message.content[0].text


def parse_unimportant(response):
    """Parse the UNIMPORTANT line from Claude's response. Returns list of email numbers (1-indexed)."""
    match = re.search(r"UNIMPORTANT:\s*(.+)", response)
    if not match:
        return []
    value = match.group(1).strip()
    if value.lower() == "none":
        return []
    try:
        return [int(n.strip()) for n in value.split(",") if n.strip().isdigit()]
    except ValueError:
        return []


def summarize_emails(auto_read=True):
    """Full pipeline: fetch unread emails, summarize via Claude, return summary.

    If auto_read is True, marks unimportant emails as read based on Claude's classification.
    """
    service = gmail.get_gmail_service()
    messages = gmail.fetch_unread_messages(service)

    if not messages:
        return "No unread emails."

    prompt_text = PROMPT_PATH.read_text()
    formatted = format_emails_for_prompt(messages)
    response = call_claude(prompt_text, formatted)

    if auto_read:
        unimportant_nums = parse_unimportant(response)
        unimportant_ids = [
            messages[n - 1]["id"]
            for n in unimportant_nums
            if 1 <= n <= len(messages)
        ]
        if unimportant_ids:
            gmail.mark_as_read(service, unimportant_ids)

    # Strip the classification lines from the user-facing summary
    summary = re.sub(r"\n*```?\n?IMPORTANT:.*\nUNIMPORTANT:.*\n?```?\n*", "", response).strip()

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize unread Gmail emails")
    parser.add_argument("--no-auto-read", action="store_true", help="Don't auto-mark unimportant emails as read")
    args = parser.parse_args()

    print(summarize_emails(auto_read=not args.no_auto_read))
