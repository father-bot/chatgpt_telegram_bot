import time

from telegram.ext import CallbackContext
from telegram import Update

from chatgpt import ChatGPT
import config


def init_user(update: Update, context: CallbackContext):
    # init chatgpt
    if "chatgpt" not in context.user_data:
        context.user_data["chatgpt"] = ChatGPT(openai_api_key=config.openai_api_key)

    if "last_interation_timestamp" not in context.user_data:
        context.user_data["last_interation_timestamp"] = time.time()
