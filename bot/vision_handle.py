import base64
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    filters,
)
import enum
import openai
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ParseMode

from openai_utils import understand_images

messages = [
    {
        "role": "user",
        "content": [],
    }
]


class State(enum.Enum):
    UPLOAD_IMAGE = 1
    DESC_TEXT = 2
    PROCESS_CONTENT = 3


def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode("utf-8")


class State(enum.Enum):
    UPLOAD_IMAGE = 1
    DESC_TEXT = 2
    PROCESS_CONTENT = 3


async def start_vision(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            KeyboardButton("VISION : Upload images"),
            KeyboardButton("VISION : Stop uploading"),
        ],
        [KeyboardButton("VISION : Restart uploading")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Choose your choice!", reply_markup=reply_markup)

    return State.UPLOAD_IMAGE


async def image_handler(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    placeholder_message = await update.message.reply_text(
        "Start to upload images!", reply_markup=None
    )

    photo_file = await update.message.photo[-1].get_file()
    image_bytes = await photo_file.download_as_bytearray()
    img_base64 = encode_image(image_bytes)

    image_message = {
        "type": "image_url",
        "image_url": f"data:image/jpeg;base64,{img_base64}",
    }
    messages[0]["content"].append(image_message)

    await context.bot.edit_message_text(
        f"Decode image successfully!",
        chat_id=placeholder_message.chat_id,
        message_id=placeholder_message.message_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=None,
    )

    await start_vision(update, context)

    return State.UPLOAD_IMAGE


async def continue_upload_image_handle(
    update: Update, context: CallbackContext
) -> None:
    if update.message.text.endswith("Stop uploading"):
        await update.message.reply_text("Say something about the image. The message must start with **VISION : **.", parse_mode=ParseMode.MARKDOWN)
        await update.message.reply_text("**VISION : **", parse_mode=ParseMode.MARKDOWN)
        return State.DESC_TEXT
    elif update.message.text.endswith("Upload images"):
        await update.message.reply_text("Please upload images!")
        return State.UPLOAD_IMAGE
    elif update.message.text.endswith("Restart uploading"):
        messages[0]["content"] = []
        await update.message.reply_text("Clean all upload images!")
        await start_vision(update, context)
        return State.UPLOAD_IMAGE
    else:
        await update.message.reply_text(
            "The option must be **Upload images** or **Stop uploading**!",
            parse_mode=ParseMode.MARKDOWN,
        )
        return State.UPLOAD_IMAGE


async def image_text_handle(update: Update, context: CallbackContext) -> None:
    filter_text = update.message.text[6:]
    text_message = {"type": "text", "text": f"{filter_text}"}
    messages[0]["content"].append(text_message)

    keyboard = [[KeyboardButton("VISION : Done")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Click the done button!", reply_markup=reply_markup)

    return State.PROCESS_CONTENT


async def done(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    placeholder_message = await update.message.reply_text("...", reply_markup=None)
    await update.message.chat.send_action(action="typing")

    try:
        text, (n_input_tokens, n_output_tokens) = await understand_images(messages)
    except openai.OpenAIError as e:
        if str(e).startswith(
            "Your request was rejected as a result of our safety system"
        ):
            text = "🥲 Your request <b>doesn't comply</b> with OpenAI's usage policies.\nWhat did you write there, huh?"
            await context.bot.edit_message_text(
                text,
                chat_id=placeholder_message.chat_id,
                message_id=placeholder_message.message_id,
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        else:
            raise

    await context.bot.edit_message_text(
        text,
        chat_id=placeholder_message.chat_id,
        message_id=placeholder_message.message_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=None,
    )

    messages[0]["content"] = []

    return ConversationHandler.END


VISION_FILTER = filters.Regex(r"^VISION")
VISION_CONVERSATION_HANDLER = ConversationHandler(
    entry_points=[CommandHandler("vision", start_vision)],
    states={
        State.UPLOAD_IMAGE: [
            MessageHandler(filters.PHOTO, image_handler),
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & VISION_FILTER,
                continue_upload_image_handle,
            ),
        ],
        State.DESC_TEXT: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & VISION_FILTER, image_text_handle
            ),
        ],
        State.PROCESS_CONTENT: [MessageHandler(filters.TEXT & VISION_FILTER, done)],
    },
    fallbacks=[CommandHandler("done", done)],
)
