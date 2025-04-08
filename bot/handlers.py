from telegram import Update
from telegram.ext import CallbackContext
from bot.registration import register_user

def start_handler(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Добро пожаловать! Пожалуйста, введите ваш табельный номер для регистрации."
    )
    context.user_data['awaiting_personnel_number'] = True

def message_handler(update: Update, context: CallbackContext):
    if context.user_data.get('awaiting_personnel_number', False):
        personnel_number = update.message.text
        register_user(update, context, personnel_number)
        context.user_data['awaiting_personnel_number'] = False