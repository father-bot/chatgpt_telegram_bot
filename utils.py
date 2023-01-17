import time

from telegram.ext import CallbackContext
from telegram import Update

from chatgpt import ChatGPT
import config


def init_user(update: Update, context: CallbackContext):
    # init chatgpt
    if "chat_context" not in context.user_data:
        context.user_data["chat_context"] = []

    if "chat_mode" not in context.user_data:
        context.user_data["chat_mode"] = "assistant"

    if "total_n_used_tokens" not in context.user_data:
        context.user_data["total_n_used_tokens"] = 0

    if "last_interation_timestamp" not in context.user_data:
        context.user_data["last_interation_timestamp"] = time.time()
