import os
import logging
import traceback
import html
import json

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    filters
)
from telegram.constants import ParseMode

from revChatGPT.revChatGPT import Chatbot

logger = logging.getLogger(__name__)

# ChatGPT
chatgpt = Chatbot({"session_token": os.environ["CHATGPT_SESSION_TOKEN"], "Authorization": ""}, conversation_id=None)
chatgpt.reset_chat()
chatgpt.refresh_session()


async def start_handler(update: Update, context: CallbackContext):
    await update.message.reply_text("I'm ChatGPT in Telegram 🤖")


async def prompt_handle(update: Update, context: CallbackContext):
    prompt = update.message.text
    r = chatgpt.get_chat_response(prompt)
    await update.message.reply_text(r["message"])


async def reset_thread_handler(update: Update, context: CallbackContext):
    chatgpt.reset_chat()
    chatgpt.refresh_session()

    await update.message.reply_text("Thread reset ✅")


async def error_handler(update: Update, context: CallbackContext) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # collect error message
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)[:2000]
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    await context.bot.send_message(update.effective_chat.id, message, parse_mode=ParseMode.HTML)


def run_bot() -> None:
    application = (
        ApplicationBuilder()
        .token(os.environ["TELEGRAM_TOKEN"])
        .build()
    )

    # add handlers
    if os.environ["ALLOWED_TELEGRAM_USERNAMES"] == "":
        user_filter = None
    else:
        allowed_usernames = list(map(str.strip, os.environ["ALLOWED_TELEGRAM_USERNAMES"].split(",")))
        user_filter = filters.User(username=allowed_usernames)

    application.add_handler(CommandHandler('start', start_handler, filters=user_filter))
    application.add_handler(CommandHandler('reset', reset_thread_handler, filters=user_filter))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & user_filter, prompt_handle))
    
    application.add_error_handler(error_handler)
    
    # start the bot
    application.run_polling()


if __name__ == "__main__":
    run_bot()
