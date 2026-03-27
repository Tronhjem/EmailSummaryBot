"""Gmail API module for fetching and managing emails.

Setup (one-time):
1. Go to https://console.cloud.google.com/ and create a project
2. Enable the Gmail API (APIs & Services > Library)
3. Create OAuth 2.0 Client ID (APIs & Services > Credentials > Desktop app)
4. Download the JSON file, rename to credentials.json, place in this directory
5. OAuth consent screen: add your Gmail as a test user
6. Run: python gmail.py
   A browser window opens for consent. After granting access, token.json is created.
"""

import base64
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
TOKEN_PATH = Path(__file__).parent / "token.json"
CREDENTIALS_PATH = Path(__file__).parent / "credentials.json"


def get_gmail_service():
    """Authenticate and return a Gmail API service object."""
    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def _extract_body(payload):
    """Recursively extract plain text body from a message payload."""
    if "parts" in payload:
        # Try to find text/plain first
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain" and part.get("body", {}).get("data"):
                return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
        # Recurse into nested parts
        for part in payload["parts"]:
            result = _extract_body(part)
            if result:
                return result
        # Fall back to text/html
        for part in payload["parts"]:
            if part["mimeType"] == "text/html" and part.get("body", {}).get("data"):
                return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
    elif payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

    return ""


def fetch_unread_messages(service, max_results=50):
    """Fetch unread messages from inbox.

    Returns list of dicts with keys: id, subject, from, date, snippet, body
    """
    results = service.users().messages().list(
        userId="me", q="is:unread", maxResults=max_results
    ).execute()

    messages_data = results.get("messages", [])
    if not messages_data:
        return []

    emails = []
    for msg_ref in messages_data:
        msg = service.users().messages().get(
            userId="me", id=msg_ref["id"], format="full"
        ).execute()

        headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
        body = _extract_body(msg["payload"])

        emails.append({
            "id": msg["id"],
            "subject": headers.get("subject", "(no subject)"),
            "from": headers.get("from", "(unknown)"),
            "date": headers.get("date", ""),
            "snippet": msg.get("snippet", ""),
            "body": body,
        })

    return emails


def mark_as_read(service, message_ids):
    """Remove UNREAD label from the given message IDs."""
    if not message_ids:
        return
    service.users().messages().batchModify(
        userId="me",
        body={"ids": message_ids, "removeLabelIds": ["UNREAD"]},
    ).execute()


if __name__ == "__main__":
    service = get_gmail_service()
    messages = fetch_unread_messages(service)
    print(f"Found {len(messages)} unread messages:")
    for msg in messages:
        print(f"  - {msg['from']}: {msg['subject']}")
