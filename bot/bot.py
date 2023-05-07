import os
import subprocess
import logging
import asyncio
import traceback
import html
import json
import tempfile
import math
import pydub
from pathlib import Path
from datetime import datetime
import openai
import telegram
from telegram import (
    Update,
    User,
    InputMediaDocument,
    InputMediaPhoto,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    AIORateLimiter,
    filters
)
from telegram.constants import ParseMode, ChatAction
import config
import database
import openai_utils
import time
# setup

db = database.Database()

logger = logging.getLogger(__name__)

user_semaphores = {}
user_tasks = {}

HELP_MESSAGE = """Comandos:
⚪ /retry - Regenera la última respuesta del bot.
⚪ /new - Iniciar nuevo diálogo.
⚪ /chat_mode - Seleccionar el modo de conversación.
⚪ /model - Mostrar configuración.
⚪ /api - Mostrar APIs.
⚪ /help – Mostrar este mensaje de nuevo.

🎨 Generar imágenes a partir de texto con <b>👩‍🎨 Artista</b> /chat_mode
👥 Añadir el bot a un <b>grupo</b>: /help_group_chat
🎤 (desactivado) Puedes enviar <b>Mensajes de voz</b> en lugar de texto.
"""

HELP_GROUP_CHAT_MESSAGE = """Puedes añadir un bot a cualquier <b>chat de grupo</b> para ayudar y entretener a sus participantes.

Instrucciones (ver <b>vídeo</b> más abajo)
1. Añade el bot al chat de grupo
2. Conviértelo en <b>administrador</b>, para que pueda ver los mensajes (el resto de derechos se pueden restringir)
3. Eres increíble!

To get a reply from the bot in the chat – @ <b>tag</b> it or <b>reply</b> to its message.
Por ejemplo: "{bot_username} escribe un poema sobre Telegram"
"""
async def reboot(update, context):
    if str(update.message.from_user.id) in config.sudo_user_id:
        await update.message.reply_text("Reiniciando...")
        subprocess.Popen(['reboot'])
    else:
        await update.message.reply_text("No permitido...")

def split_text_into_chunks(text, chunk_size):
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]

async def register_user_if_not_exists(update: Update, context: CallbackContext, user=None):
    if user is None:
        if update.message is None:
            user = update.callback_query.from_user
        elif update.callback_query is None:
            user = update.message.from_user
    
    if not db.check_if_user_exists(user.id):
        db.add_new_user(
            user.id,
            update.message.chat_id,
            username=user.username,
            first_name=user.first_name,
            last_name= user.last_name
        )
        db.start_new_dialog(user.id)

    if db.get_user_attribute(user.id, "current_dialog_id") is None:
        db.start_new_dialog(user.id)

    if user.id not in user_semaphores:
        user_semaphores[user.id] = asyncio.Semaphore(1)

    if db.get_user_attribute(user.id, "current_model") is None:
        db.set_user_attribute(user.id, "current_model", config.model["available_model"][0])
        
    if db.get_user_attribute(user.id, "current_api") is None:
        db.set_user_attribute(user.id, "current_api", config.api["available_api"][0])

async def is_bot_mentioned(update: Update, context: CallbackContext):
     try:
         message = update.message

         if message.chat.type == "private":
             return True

         if message.text is not None and ("@" + context.bot.username) in message.text:
             return True

         if message.reply_to_message is not None:
             if message.reply_to_message.from_user.id == context.bot.id:
                 return True
     except:
         return True
     else:
         return False

async def start_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update, context, update.message.from_user)
    user_id = update.message.from_user.id

    db.set_user_attribute(user_id, "last_interaction", datetime.now())
    await new_dialog_handle(update, context)

    reply_text = "Hola! Soy <b>ChatGPT</b> bot implementado con la API de OpenAI.🤖\n\n"
    reply_text += HELP_MESSAGE

    await update.message.reply_text(reply_text, parse_mode=ParseMode.HTML)
    await chat_mode_handle(update, context)

async def help_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update, context, update.message.from_user)
    user_id = update.message.from_user.id
    db.set_user_attribute(user_id, "last_interaction", datetime.now())
    await update.message.reply_text(HELP_MESSAGE, parse_mode=ParseMode.HTML)

async def help_group_chat_handle(update: Update, context: CallbackContext):
     await register_user_if_not_exists(update, context, update.message.from_user)
     user_id = update.message.from_user.id
     db.set_user_attribute(user_id, "last_interaction", datetime.now())

     text = HELP_GROUP_CHAT_MESSAGE.format(bot_username="@" + context.bot.username)

     await update.message.reply_text(text, parse_mode=ParseMode.HTML)
     await update.message.reply_video(config.help_group_chat_video_path)

async def retry_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update, context, update.message.from_user)
    #if await is_previous_message_not_answered_yet(update, context): return

    user_id = update.message.from_user.id
    db.set_user_attribute(user_id, "last_interaction", datetime.now())

    dialog_messages = db.get_dialog_messages(user_id, dialog_id=None)
    if len(dialog_messages) == 0:
        await update.message.reply_text("No hay mensaje para reintentar 🤷‍♂️")
        return

    last_dialog_message = dialog_messages.pop()
    db.set_dialog_messages(user_id, dialog_messages, dialog_id=None)  # last message was removed from the context

    await message_handle(update, context, message=last_dialog_message["user"], use_new_dialog_timeout=False)

async def message_handle(update: Update, context: CallbackContext, message=None, use_new_dialog_timeout=True):
    # check if bot was mentioned (for group chats)
    if not await is_bot_mentioned(update, context):
        return

    # check if message is edited
    if update.edited_message is not None:
        await edited_message_handle(update, context)
        return

    _message = message or update.message.text

    # remove bot mention (in group chats)
    if update.message.chat.type != "private":
        _message = _message.replace("@" + context.bot.username, "").strip()

    await register_user_if_not_exists(update, context, user=None)
    if await is_previous_message_not_answered_yet(update, context): return

    user_id = update.message.from_user.id
    chat_mode = db.get_user_attribute(user_id, "current_chat_mode")

    if chat_mode == "artist":
        await generate_image_handle(update, context, message=message)
        return

    async def message_handle_fn():
        # new dialog timeout
        if use_new_dialog_timeout:
            if (datetime.now() - db.get_user_attribute(user_id, "last_interaction")).seconds > config.new_dialog_timeout and len(db.get_dialog_messages(user_id)) > 0:
                await new_dialog_handle(update, context)
                await update.message.reply_text(f"Starting new dialog due to timeout (<b>{config.chat_mode['info'][chat_mode]['name']}</b> mode) ✅", parse_mode=ParseMode.HTML)
        db.set_user_attribute(user_id, "last_interaction", datetime.now())

        # in case of CancelledError
        current_model = db.get_user_attribute(user_id, "current_model")

        try:
            # send placeholder message to user
            placeholder_message = await update.message.reply_text("...")

            # send typing action
            await update.message.chat.send_action(action="typing")

            if _message is None or len(_message) == 0:
                 await update.message.reply_text("🥲 You sent <b>empty message</b>. Please, try again!", parse_mode=ParseMode.HTML)
                 return

            dialog_messages = db.get_dialog_messages(user_id, dialog_id=None)
            parse_mode = {
                "html": ParseMode.HTML,
                "markdown": ParseMode.MARKDOWN
            }[config.chat_mode["info"][chat_mode]["parse_mode"]]
            chatgpt_instance = openai_utils.ChatGPT(model=current_model)
            gen = chatgpt_instance.send_message(_message, user_id, dialog_messages=dialog_messages, chat_mode=chat_mode)     
            prev_answer = ""
            async for status, gen_answer in gen:                                                         
                answer = gen_answer[:4096]  # telegram message limit                                     
                                                                                                        
                # update only when 100 new symbols are ready                                             
                if abs(len(answer) - len(prev_answer)) < 75 and status != "finished":                    
                    continue                                                                             
                try:                                                                                     
                    await context.bot.edit_message_text(answer, chat_id=placeholder_message.chat_id, message_id=placeholder_message.message_id, parse_mode=parse_mode)                                
                except telegram.error.BadRequest as e:                                                   
                    if str(e).startswith("Message is not modified"):                                     
                        continue                                                                         
                    else:                                                                                
                        await context.bot.edit_message_text(answer, chat_id=placeholder_message.chat_id, message_id=placeholder_message.message_id)                                                       
                await asyncio.sleep(0.5)  # wait a bit to avoid flooding                                 
                                                                                                        
                prev_answer = answer
            # update user data
            new_dialog_message = {"user": _message, "bot": answer, "date": datetime.now()}
            db.set_dialog_messages(
                user_id,
                db.get_dialog_messages(user_id, dialog_id=None) + [new_dialog_message],
                dialog_id=None
            )

        
        except Exception as e:
            error_text = f"{e}"
            logger.error(error_text)
            await update.message.reply_text(error_text)
            return
        if chat_mode == "imagen":
            await generate_image_handle(update, context, message=answer)
            return
        
    async with user_semaphores[user_id]:
        task = asyncio.create_task(message_handle_fn())
        user_tasks[user_id] = task

        try:
            await task
        except asyncio.CancelledError:
            await update.message.reply_text("✅ Canceled", parse_mode=ParseMode.HTML)
        else:
            pass
        finally:
            if user_id in user_tasks:
                del user_tasks[user_id]

async def is_previous_message_not_answered_yet(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update, context, update.message.from_user)

    user_id = update.message.from_user.id
    semaphore = user_semaphores.get(user_id)
    if semaphore and semaphore.locked():
        text = "⏳ Por favor <b>espera</b> una respuesta al mensaje anterior\n"
        text += "O puedes /cancel"
        await update.message.reply_text(text, reply_to_message_id=update.message.id, parse_mode=ParseMode.HTML)
        return True
    else:
        return False

async def voice_message_handle(update: Update, context: CallbackContext):
    # check if bot was mentioned (for group chats)
    if not await is_bot_mentioned(update, context):
        return

    await register_user_if_not_exists(update, context, update.message.from_user)
    #if await is_previous_message_not_answered_yet(update, context): return

    user_id = update.message.from_user.id
    db.set_user_attribute(user_id, "last_interaction", datetime.now())

    voice = update.message.voice
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        voice_ogg_path = tmp_dir / "voice.ogg"

        # download
        voice_file = await context.bot.get_file(voice.file_id)
        await voice_file.download_to_drive(voice_ogg_path)
        # convert to mp3
        voice_mp3_path = tmp_dir / "voice.mp3"
        pydub.AudioSegment.from_file(voice_ogg_path).export(voice_mp3_path, format="mp3")
        # transcribe
        transcribed_text = await openai_utils.transcribe_audio(str(voice_ogg_path))
        if transcribed_text is None:
            transcribed_text = ""

    text = f"🎤: <i>{transcribed_text}</i>"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

    await message_handle(update, context, message=transcribed_text)

async def generate_image_handle(update: Update, context: CallbackContext, message=None):
    await register_user_if_not_exists(update, context, update.message.from_user)

    user_id = update.message.from_user.id
    db.set_user_attribute(user_id, "last_interaction", datetime.now())

    await update.message.chat.send_action(action="upload_photo")

    prompt = message or update.message.text

    try:
        image_urls = await openai_utils.generate_images(prompt, user_id)
    except openai.error.InvalidRequestError as e:
        if str(e).startswith("Su solicitud fue rechazada como resultado de nuestro sistema de seguridad"):
            text = "🥲 Tu solicitud <b>no cumple</b> con las políticas de uso de OpenAI.</b> ¿Qué has escrito ahí, eh?"
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
            return
        else:
            raise
    media_group=[]
    for i, image_url in enumerate(image_urls):
        media = InputMediaPhoto(image_url)
        media_group.append(media)
    await update.message.chat.send_action(action="upload_photo")
    await update.message.reply_media_group(media_group)
    
    media_group=[]
    for i, image_url in enumerate(image_urls):
        media = InputMediaDocument(image_url, parse_mode=ParseMode.HTML, filename=f"imagen_{i}.png")
        media_group.append(media)

    await update.message.chat.send_action(action="upload_document")
    await update.message.reply_media_group(media_group)

async def new_dialog_handle(update: Update, context: CallbackContext, user=None):
    if update.message is None:
        user = update.callback_query.from_user
    elif update.callback_query is None:
        user = update.message.from_user
    
    await register_user_if_not_exists(update, context)
    #if await is_previous_message_not_answered_yet(update, context): return

    user_id = user.id
    db.set_user_attribute(user_id, "last_interaction", datetime.now())
    
    api_actual = db.get_user_attribute(user_id, 'current_api')
    modelo_actual = db.get_user_attribute(user_id, 'current_model')
    mododechat_actual=db.get_user_attribute(user_id, 'current_chat_mode')

    
    # Verificar si hay valores inválidos en el usuario
    if (mododechat_actual not in config.chat_mode["available_chat_mode"] or api_actual not in config.api["available_api"] or modelo_actual not in config.model["available_model"]):
        db.reset_user_attribute(user_id)
        await update.message.reply_text(update, "Tenías un parámetro no válido en la configuración, por lo que se ha restablecido todo a los valores predeterminados.")

    modelos_disponibles=config.api["info"][api_actual]["available_model"]
    apisconimagen=config.api["available_imagen"]
    api_actual_name=config.api["info"][api_actual]["name"]
    
    # Verificar si el modelo actual es válido en la API actual
    if modelo_actual not in modelos_disponibles:
        db.set_user_attribute(user_id, "current_model", modelos_disponibles[0])
        await send_reply(update, f'Tu modelo actual no es compatible con la API "{api_actual_name}", por lo que se ha cambiado el modelo automáticamente a "{config.model["info"][db.get_user_attribute(user_id, "current_model")]["name"]}".')

    # Verificar si la API actual es soporta imágenes:
    if mododechat_actual in ["imagen", "artist"] and api_actual not in apisconimagen:
        db.set_user_attribute(user_id, "current_api", apisconimagen[0])
        await send_reply(update, f'Tu API actual "{api_actual_name}" no soporta imágenes, por lo que se ha cambiado automáticamente a "{config.api["info"][db.get_user_attribute(user_id, "current_api")]["name"]}"')

    db.start_new_dialog(user_id)
    #Bienvenido!   
    await send_reply(update, f"{config.chat_mode['info'][db.get_user_attribute(user.id, 'current_chat_mode')]['welcome_message']}")

async def send_reply(update, text, parse_mode=ParseMode.HTML):
    if update.callback_query:
        chat_id = update.effective_chat.id
        await update.effective_chat.send_message(text=text, parse_mode=parse_mode)
    else:
        await update.message.reply_text(text=text, parse_mode=parse_mode)

async def cancel_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update, context, update.message.from_user)

    user_id = update.message.from_user.id
    db.set_user_attribute(user_id, "last_interaction", datetime.now())

    if user_id in user_tasks:
        task = user_tasks[user_id]
        task.cancel()
    else:
        await update.message.reply_text("<i>No hay nada que cancelar...</i>", parse_mode=ParseMode.HTML)

async def get_menu(update: Update, user_id: int, menu_type: str):
    menu_type_dict = getattr(config, menu_type)
    if menu_type == "model":
        modelos_disponibles = config.api["info"][db.get_user_attribute(user_id, "current_api")]["available_model"]
        if db.get_user_attribute(user_id, 'current_model') not in modelos_disponibles:
            api_actual = db.get_user_attribute(user_id, 'current_api')
            db.set_user_attribute(user_id, "current_model", modelos_disponibles[0])
            await send_reply(update, f'Tu modelo actual no es compatible con la API "{config.api["info"][api_actual]["name"]}", por lo que se ha cambiado el modelo automáticamente a "{config.model["info"][db.get_user_attribute(user_id, "current_model")]["name"]}".')
            pass
        item_keys = config.api["info"][db.get_user_attribute(user_id, "current_api")]["available_model"]
    else:
        item_keys = menu_type_dict[f"available_{menu_type}"]
        
    current_key = db.get_user_attribute(user_id, f"current_{menu_type}")
    
    text = "<b>Actual:</b>\n\n" + menu_type_dict["info"][current_key]["name"] + ", " + menu_type_dict["info"][current_key]["description"] + "\n\n<b>Selecciona un " + f"{menu_type}" + " disponible</b>:"

    num_cols = 2
    num_rows = math.ceil(len(item_keys) / num_cols)
    options = [[menu_type_dict["info"][current_key]["name"], f"set_{menu_type}|{current_key}", current_key] for current_key in item_keys]
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(name, callback_data=data) 
                for name, data, selected in options[i::num_rows]
            ]
            for i in range(num_rows)
        ]
    )

    return text, reply_markup

async def chat_mode_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update, context, update.message.from_user)
    #if await is_previous_message_not_answered_yet(update, context): return

    user_id = update.message.from_user.id
    db.set_user_attribute(user_id, "last_interaction", datetime.now())
    
    text, reply_markup = await get_menu(update, user_id, "chat_mode")
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def chat_mode_callback_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update.callback_query, context, update.callback_query.from_user, force=False)
    #if await is_previous_message_not_answered_yet(update.callback_query, context): return

    user_id = update.callback_query.from_user.id
    db.set_user_attribute(user_id, "last_interaction", datetime.now())
    query = update.callback_query
    await query.answer()


    text, reply_markup = await get_menu(update, user_id, "chat_mode")
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except telegram.error.BadRequest as e:
        if str(e).startswith("El mensaje no se modifica"):
            pass

async def set_chat_mode_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update.callback_query, context, update.callback_query.from_user)
    user_id = update.callback_query.from_user.id

    query = update.callback_query
    await query.answer()

    mode = query.data.split("|")[1]

    db.set_user_attribute(user_id, "current_chat_mode", mode)
    await new_dialog_handle(update, context)

async def model_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update, context, update.message.from_user)
    #if await is_previous_message_not_answered_yet(update, context): return

    user_id = update.message.from_user.id
    db.set_user_attribute(user_id, "last_interaction", datetime.now())

    text, reply_markup = await get_menu(update, user_id, "model")
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def model_callback_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update.callback_query, context, update.callback_query.from_user)
    #if await is_previous_message_not_answered_yet(update.callback_query, context): return

    user_id = update.callback_query.from_user.id
    db.set_user_attribute(user_id, "last_interaction", datetime.now())

    query = update.callback_query
    await query.answer()

    text, reply_markup = await get_menu(update, user_id, "model")
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except telegram.error.BadRequest as e:
        if str(e).startswith("El mensaje no se modifica"):
            pass

async def set_model_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update.callback_query, context, update.callback_query.from_user)
    user_id = update.callback_query.from_user.id

    query = update.callback_query
    await query.answer()

    _, model = query.data.split("|")
    db.set_user_attribute(user_id, "current_model", model)
    await new_dialog_handle(update, context)

    text, reply_markup = await get_menu(update, user_id, "model")
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except telegram.error.BadRequest as e:
        if str(e).startswith("El mensaje no se modifica"):
            pass

async def api_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update, context, update.message.from_user)
    #if await is_previous_message_not_answered_yet(update, context): return

    user_id = update.message.from_user.id
    db.set_user_attribute(user_id, "last_interaction", datetime.now())

    text, reply_markup = await get_menu(update, user_id, "api")
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def api_callback_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update.callback_query, context, update.callback_query.from_user)
    #if await is_previous_message_not_answered_yet(update.callback_query, context): return

    user_id = update.callback_query.from_user.id
    db.set_user_attribute(user_id, "last_interaction", datetime.now())

    query = update.callback_query
    await query.answer()

    text, reply_markup = await get_menu(update, user_id, "api")
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except telegram.error.BadRequest as e:
        if str(e).startswith("El mensaje no se modifica"):
            pass

async def set_api_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update.callback_query, context, update.callback_query.from_user)
    user_id = update.callback_query.from_user.id
    query = update.callback_query
    await query.answer()

    _, api = query.data.split("|")
    db.set_user_attribute(user_id, "current_api", api)

    # check if there is an ongoing dialog
    current_dialog = db.get_user_attribute(user_id, "current_dialog")
    if current_dialog is not None:
        await query.message.reply_text("Por favor, termina tu conversación actual antes de iniciar una nueva.")
        return

    await new_dialog_handle(update, context)

    text, reply_markup = await get_menu(update, user_id, "api")
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except telegram.error.BadRequest as e:
        if str(e).startswith("El mensaje no se modifica"):
            pass

async def edited_message_handle(update: Update, context: CallbackContext):
    if update.edited_message.chat.type == "private":
        text = "🥲 Lamentablemente, no es posible <b>editar mensajes</b>."
        await update.edited_message.reply_text(text, parse_mode=ParseMode.HTML)

async def error_handle(update: Update, context: CallbackContext) -> None:
    logger.error(msg="Excepción al gestionar una actualización:", exc_info=context.error)

    try:
        # collect error message
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)
        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        message = (
            f"Excepción al gestionar una actualización\n"
            f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
            "</pre>\n\n"
            f"<pre>{html.escape(tb_string)}</pre>"
        )

        # # split text into multiple messages due to 4096 character limit
        # for message_chunk in split_text_into_chunks(message, 4096):
        #     try:
        #         await context.bot.send_message(update.effective_chat.id, message_chunk, parse_mode=ParseMode.HTML)
        #     except telegram.error.BadRequest:
        #         # answer has invalid characters, so we send it without parse_mode
        #         await context.bot.send_message(update.effective_chat.id, message_chunk)
    except:
        await context.bot.send_message("Algún error en el gestor de errores")

async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("/new", "Iniciar un nuevo diálogo"),
        BotCommand("/chat_mode", "Cambia el modo de asistente"),
        BotCommand("/retry", "Re-generar respuesta para la consulta anterior"),
        BotCommand("/model", "Mostrar ajustes"),
        BotCommand("/api", "Mostrar APIs"),
        BotCommand("/help", "Ver mensaje de ayuda"),
    ])

def run_bot() -> None:
    application = (
        ApplicationBuilder()
        .token(config.telegram_token)
        .concurrent_updates(True)
        .rate_limiter(AIORateLimiter(max_retries=5))
        .post_init(post_init)
        .build()
    )

    # add handlers
    user_filter = filters.ALL
    if len(config.allowed_telegram_usernames) > 0:
        usernames = [x for x in config.allowed_telegram_usernames if isinstance(x, str)]
        user_ids = [x for x in config.allowed_telegram_usernames if isinstance(x, int)]
        user_filter = filters.User(username=usernames) | filters.User(user_id=user_ids)



    application.add_handler(CommandHandler("start", start_handle, filters=user_filter))
    application.add_handler(CommandHandler("help", help_handle, filters=user_filter))
    application.add_handler(CommandHandler("help_group_chat", help_group_chat_handle, filters=user_filter))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & user_filter, message_handle))
    application.add_handler(CommandHandler("retry", retry_handle, filters=user_filter))
    application.add_handler(CommandHandler("new", new_dialog_handle, filters=user_filter))
    application.add_handler(CommandHandler("cancel", cancel_handle, filters=user_filter))

    application.add_handler(MessageHandler(filters.VOICE & user_filter, voice_message_handle))

    application.add_handler(CommandHandler("chat_mode", chat_mode_handle, filters=user_filter))
    application.add_handler(CommandHandler("model", model_handle, filters=user_filter))
    application.add_handler(CommandHandler("api", api_handle, filters=user_filter))
    
    application.add_handler(CommandHandler('reboot', reboot, filters=user_filter))

    application.add_handler(CallbackQueryHandler(chat_mode_callback_handle, pattern="^get_menu"))
    application.add_handler(CallbackQueryHandler(set_chat_mode_handle, pattern="^set_chat_mode"))

    application.add_handler(CallbackQueryHandler(model_callback_handle, pattern="^get_menu"))
    application.add_handler(CallbackQueryHandler(set_model_handle, pattern="^set_model"))

    application.add_handler(CallbackQueryHandler(api_callback_handle, pattern="^get_menu"))
    application.add_handler(CallbackQueryHandler(set_api_handle, pattern="^set_api"))
    application.add_error_handler(error_handle)

    # start the bot
    application.run_polling()

if __name__ == "__main__":
    run_bot()
