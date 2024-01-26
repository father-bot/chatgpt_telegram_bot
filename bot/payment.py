from telegram import LabeledPrice, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import os
from datetime import date
from database import Database
import config
from config import donates

db = Database()

#grab donate levels from donates.yml

async def generate_payment(update: Update, context: CallbackContext):
  update.callback_query.answer()
  donate_level = update.callback_query.data.split("|")[1]
  donate = donates[donate_level]
  await send_payment_message(
    update, 
    context, 
    donate["name"], 
    donate["description"], 
    donate_level, 
    donate["name"], 
    donate["price"]*100
    )

async def send_payment_message(update: Update, context: CallbackContext, title, description, payload, name, price):
  await context.bot.send_invoice(
    chat_id = update.effective_chat.id, 
    title=title, 
    description = description, 
    payload = payload,
    provider_token = config.payment_token,
    currency = "RUB",
    prices = [LabeledPrice(name, price)]
    )

async def handle_precheckout(update: Update, context: CallbackContext):
  pre_checkout_query = update.pre_checkout_query
  ok : bool = True
  error_message: str = ""
  """check whether everything is alright here and let the user continue the purchase if so, otherwise abort"""
  await pre_checkout_query.answer(ok, error_message)
  
async def handle_payment(update: Update, context: CallbackContext) -> None:
    """Confirms the successful payment."""
    current_tokens = db.get_user_attribute(update.effective_user.id, "n_total_tokens")
    donate_level = update.message.successful_payment.invoice_payload
    db.set_user_attribute(update.effective_user.id, "n_total_tokens", current_tokens + donates[donate_level]["token_amount"])