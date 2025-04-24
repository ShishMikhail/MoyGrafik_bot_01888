import sys
import os
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from sqlalchemy import text

# Добавляем корень проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from database.db import engine, user_settings
from bot.utils import INPUT_CLID

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало процесса регистрации. Запрашивает табельный номер."""
    await update.message.reply_text("Пожалуйста, введи свой табельный номер (только цифры).")
    return INPUT_CLID

async def process_clid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает введённый табельный номер и регистрирует пользователя."""
    user = update.effective_user
    telegram_id = user.id
    clid = update.message.text

    # Проверяем, что введены только цифры
    if not clid.isdigit():
        await update.message.reply_text("Табельный номер должен содержать только цифры. Попробуй снова.")
        return INPUT_CLID

    with engine.connect() as connection:
        # Ищем сотрудника по clid
        query = text("""
            SELECT id, first_name, last_name
            FROM employees
            WHERE clid = :clid AND timezone_id = 516
        """)
        result = connection.execute(query, {"clid": clid}).mappings().fetchone()

        if not result:
            await update.message.reply_text(
                "Сотрудник с таким табельным номером не найден или не относится к часовому поясу Владивосток. Проверь номер и попробуй снова."
            )
            return INPUT_CLID

        employee_id = result['id']
        first_name = result['first_name']
        last_name = result['last_name']

        # Проверяем, не зарегистрирован ли уже этот telegram_id
        query = text("SELECT employee_id FROM user_settings WHERE telegram_id = :telegram_id")
        existing = connection.execute(query, {"telegram_id": telegram_id}).fetchone()

        if existing:
            await update.message.reply_text("Ты уже зарегистрирован под другим табельным номером.")
            return ConversationHandler.END

        # Регистрируем пользователя
        query = text("""
            INSERT INTO user_settings (telegram_id, employee_id, subscribed, notification_times)
            VALUES (:telegram_id, :employee_id, TRUE, '[]')
            ON CONFLICT (telegram_id) DO NOTHING
        """)
        connection.execute(query, {"telegram_id": telegram_id, "employee_id": employee_id})
        connection.commit()

        await update.message.reply_text(
            f"Регистрация успешна, {first_name} {last_name}! Теперь ты можешь использовать /menu для настроек."
        )
        return ConversationHandler.END