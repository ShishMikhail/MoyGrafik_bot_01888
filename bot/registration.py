from telegram import Update
from telegram.ext import CallbackContext
import sqlite3

def register_user(update: Update, context: CallbackContext, personnel_number: str):
    telegram_id = update.message.chat_id

    with sqlite3.connect('your_database.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE personnel_number = ?",
            (personnel_number,)
        )
        user = cursor.fetchone()

        if user:
            cursor.execute(
                "UPDATE users SET telegram_id = ? WHERE personnel_number = ?",
                (telegram_id, personnel_number)
            )
            conn.commit()
            update.message.reply_text("Вы успешно зарегистрированы!")
        else:
            update.message.reply_text("Пользователь с таким табельным номером не найден.")