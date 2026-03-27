import os
import logging

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Bot is running. Your chat ID is: {chat_id}")
    logger.info(f"/start from chat_id={chat_id}")


async def emails_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    logger.info(f"/emails from chat_id={chat_id}")
    await update.message.reply_text("Fetching and summarizing emails...")

    try:
        from summarize_emails import summarize_emails
        summary = summarize_emails(auto_read=True)

        # Telegram messages max 4096 chars — split if needed
        while summary:
            chunk, summary = summary[:4096], summary[4096:]
            await update.message.reply_text(chunk)
    except Exception as e:
        logger.error(f"Email summary failed: {e}")
        await update.message.reply_text(f"Error: {e}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    text = update.message.text
    logger.info(f"[{chat_id}] {user.first_name}: {text}")


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("emails", emails_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
