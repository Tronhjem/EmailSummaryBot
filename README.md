# Telegram Automation Bot

A Python Telegram bot that fetches unread Gmail messages, summarizes them using Claude CLI, and auto-marks unimportant emails as read.

## Features

- Fetch and summarize unread emails via Claude AI
- Auto-classify emails as important/unimportant
- Unimportant emails are automatically marked as read
- Customizable prompt template for email categorization
- Trigger via Telegram (`/emails`), CLI, or cron job
- Send messages to Telegram from the command line

## Setup

### 1. Clone and create virtual environment

```bash
git clone git@github.com:Tronhjem/telegramAutomationBot.git
cd telegramAutomationBot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Create the Telegram bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Choose a name and username (must end in `bot`)
4. Copy the bot token

### 3. Configure environment

Create a `.env` file in the project root:

```
BOT_TOKEN=your-telegram-bot-token
CHAT_ID=
```

Start the bot (`python bot.py`), then send `/start` to your bot in Telegram. It will reply with your chat ID. Add it to `.env`:

```
CHAT_ID=your-chat-id
```

### 4. Set up Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create a project
2. Enable the **Gmail API** (APIs & Services > Library)
3. Go to APIs & Services > Credentials > Create Credentials > **OAuth 2.0 Client ID**
4. Application type: **Desktop app**
5. Download the JSON file, rename it to `credentials.json`, and place it in the project root
6. Go to APIs & Services > OAuth consent screen > add your Gmail as a **test user**
7. Run `python gmail.py` — a browser window opens for consent. After granting access, `token.json` is created automatically

### 5. Install Claude CLI

The email summarization uses [Claude Code](https://claude.ai/claude-code) CLI. Install it and make sure `claude` is available in your PATH.

## Usage

### Telegram commands

| Command | Description |
|---------|-------------|
| `/start` | Check bot is running, shows your chat ID |
| `/emails` | Fetch unread emails, summarize, and send the result |

### CLI

```bash
# Summarize emails (auto-marks unimportant as read)
python summarize_emails.py

# Summarize without marking anything as read
python summarize_emails.py --no-auto-read

# Send a message to Telegram
python send.py "Hello from terminal"

# Test Gmail connection
python gmail.py
```

### Cron job

To get email summaries on a schedule, add to your crontab (`crontab -e`):

```
# Every morning at 8am
0 8 * * * /path/to/telegramAutomationBot/cron_emails.sh
```

## Customization

Edit `prompts/email_summary.md` to change how Claude categorizes and formats the email summary. The default categories are:

- Action Required
- Important
- Newsletters & Updates
- Notifications
- Sales & Offers
- Spam / Low Priority

## Project structure

```
bot.py                  # Telegram bot with polling
send.py                 # CLI message sender
gmail.py                # Gmail API module
summarize_emails.py     # Email fetch + Claude summarization
cron_emails.sh          # Cron-friendly wrapper script
prompts/
  email_summary.md      # Editable Claude prompt template
```
