import os
import logging
import traceback
import html
import json
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    PicklePersistence,
    CallbackQueryHandler,
    filters
)
from telegram.constants import ParseMode, ChatAction

import chatgpt
import utils
import config


# setup
logger = logging.getLogger(__name__)

HELP_MESSAGE = """Commands:
⚪ /retry – Regenerate last bot answer
⚪ /new – Start new dialog
⚪ /mode – Select chat mode
⚪ /balance – Show balance
⚪ /help – Show help
"""


async def start_handle(update: Update, context: CallbackContext):
    utils.init_user(update, context)
    context.user_data["last_interation_timestamp"] = time.time()

    reply_text = "Hi! I'm <b>ChatGPT</b> bot implemented with GPT-3.5 OpenAI API 🤖\n\n"
    reply_text += HELP_MESSAGE

    reply_text += "\nAnd now... ask me anything!"
    
    await update.message.reply_text(reply_text, parse_mode=ParseMode.HTML)


async def help_handle(update: Update, context: CallbackContext):
    utils.init_user(update, context)
    context.user_data["last_interation_timestamp"] = time.time()
    await update.message.reply_text(HELP_MESSAGE, parse_mode=ParseMode.HTML)


async def retry_handle(update: Update, context: CallbackContext):
    context.user_data["last_interation_timestamp"] = time.time()

    if len(context.user_data["chat_context"]) == 0:
        await update.message.reply_text("No message to retry 🤷‍♂️")
        return

    last_chat_context_item = context.user_data["chat_context"].pop()
    await message_handle(update, context, message=last_chat_context_item["user"], use_new_dialog_timeout=False)


async def message_handle(update: Update, context: CallbackContext, message=None, use_new_dialog_timeout=True):
    utils.init_user(update, context)

    # new dialog timeout
    if use_new_dialog_timeout:
        if time.time() - context.user_data["last_interation_timestamp"] > config.new_dialog_timeout:
            context.user_data["chat_context"] = []
            await update.message.reply_text("Starting new dialog due to timeout ✅")
    context.user_data["last_interation_timestamp"] = time.time()

    # send typing action
    await update.message.chat.send_action(action="typing")

    try:
        message = message or update.message.text
        answer, prompt, chat_context, n_used_tokens, n_first_chat_context_messages_removed = chatgpt.ChatGPT().send_message(
            message,
            chat_context=context.user_data["chat_context"],
            chat_mode=context.user_data["chat_mode"]
        )
    except Exception as e:
        error_text = f"Something went wrong during completion. Reason: {e}"
        logger.error(error_text)
        await update.message.reply_text(error_text)
        return

    # update user data
    context.user_data["chat_context"] = chat_context
    context.user_data["total_n_used_tokens"] += n_used_tokens

    # send message if some messages were removed from the context
    if n_first_chat_context_messages_removed > 0:
        if n_first_chat_context_messages_removed == 1:
            text = "✍️ <i>Note:</i> Your current dialog is too long, so your <b>first message</b> was removed from the context.\n Send /new command to start new dialog"
        else:
            text = f"✍️ <i>Note:</i> Your current dialog is too long, so <b>{n_first_chat_context_messages_removed} first messages</b> were removed from the context.\n Send /new command to start new dialog"
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)

    await update.message.reply_text(answer, parse_mode=ParseMode.HTML)


async def new_dialog_handle(update: Update, context: CallbackContext):
    utils.init_user(update, context)
    context.user_data["last_interation_timestamp"] = time.time()

    context.user_data["chat_context"] = []
    await update.message.reply_text("Starting new dialog ✅")

    chat_mode = context.user_data["chat_mode"]
    await update.message.reply_text(f"{chatgpt.CHAT_MODES[chat_mode]['welcome_message']}", parse_mode=ParseMode.HTML)


async def show_chat_modes_handle(update: Update, context: CallbackContext):
    utils.init_user(update, context)
    context.user_data["last_interation_timestamp"] = time.time()

    keyboard = []
    for chat_mode, chat_mode_dict in chatgpt.CHAT_MODES.items():
        keyboard.append([InlineKeyboardButton(chat_mode_dict["name"], callback_data=f"set_chat_mode|{chat_mode}")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Select chat mode:", reply_markup=reply_markup)


async def set_chat_mode_handle(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    chat_mode = query.data.split("|")[1]

    context.user_data["chat_mode"] = chat_mode
    context.user_data["chat_context"] = []

    await query.edit_message_text(
        f"<b>{chatgpt.CHAT_MODES[chat_mode]['name']}</b> chat mode is set",
        parse_mode=ParseMode.HTML
    )

    await query.edit_message_text(f"{chatgpt.CHAT_MODES[chat_mode]['welcome_message']}", parse_mode=ParseMode.HTML)


async def show_balance_handle(update: Update, context: CallbackContext):
    utils.init_user(update, context)
    context.user_data["last_interation_timestamp"] = time.time()

    total_n_used_tokens = context.user_data['total_n_used_tokens']
    total_spent_dollars = total_n_used_tokens * (0.01 / 1000)

    text = f"You spent <b>{total_spent_dollars:.03f}$</b>\n"
    text += f"You used <b>{total_n_used_tokens}</b> tokens <i>(price: 0.01$ per 1000 tokens)</i>\n"

    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


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
    persistence = PicklePersistence(filepath=config.persistence_path)

    application = (
        ApplicationBuilder()
        .token(config.telegram_token)
        .persistence(persistence)
        .build()
    )

    # add handlers
    if len(config.allowed_telegram_usernames) == 0:
        user_filter = filters.ALL
    else:
        user_filter = filters.User(username=config.allowed_telegram_usernames)

    application.add_handler(CommandHandler("start", start_handle, filters=user_filter))
    application.add_handler(CommandHandler("help", help_handle, filters=user_filter))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & user_filter, message_handle))
    application.add_handler(CommandHandler("retry", retry_handle, filters=user_filter))
    application.add_handler(CommandHandler("new", new_dialog_handle, filters=user_filter))
    
    application.add_handler(CommandHandler("mode", show_chat_modes_handle, filters=user_filter))
    application.add_handler(CallbackQueryHandler(set_chat_mode_handle, pattern="^set_chat_mode"))

    application.add_handler(CommandHandler("balance", show_balance_handle, filters=user_filter))
    
    application.add_error_handler(error_handler)
    
    # start the bot
    application.run_polling()


if __name__ == "__main__":
    run_bot()
