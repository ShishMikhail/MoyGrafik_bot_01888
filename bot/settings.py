import json
import sys
import os
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from sqlalchemy import text, select, update, insert
from sqlalchemy.exc import SQLAlchemyError
import logging

# Добавляем корень проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from database.db import engine, user_settings
from bot.utils import INPUT_VACATION_START, INPUT_VACATION_END, INPUT_ARRIVAL_NOTIFICATION_TIME, INPUT_DEPARTURE_NOTIFICATION_TIME

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler('settings.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_user_settings(telegram_id):
    """
    Получение настроек пользователя по telegram_id.
    Возвращает: (subscribed, vacation_start, vacation_end, arrival_notification_times, departure_notification_times)
    """
    try:
        with engine.connect() as conn:
            query = select(user_settings).where(user_settings.c.telegram_id == telegram_id)
            result = conn.execute(query).mappings().fetchone()
            if result:
                subscribed = result['subscribed']
                vacation_start = result['vacation_start']
                vacation_end = result['vacation_end']
                arrival_notification_times = json.loads(result['arrival_notification_times']) if result['arrival_notification_times'] else []
                departure_notification_times = json.loads(result['departure_notification_times']) if result['departure_notification_times'] else []
                return subscribed, vacation_start, vacation_end, arrival_notification_times, departure_notification_times
            return False, None, None, [], []  # Значения по умолчанию, если пользователь не найден
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении настроек пользователя {telegram_id}: {e}")
        return False, None, None, [], []

def update_user_settings(telegram_id, subscribed=None, vacation_start=None, vacation_end=None, arrival_notification_times=None, departure_notification_times=None):
    """
    Обновление настроек пользователя в таблице user_settings.
    """
    try:
        with engine.connect() as conn:
            # Проверяем, существует ли пользователь, если нет — создаём запись
            query = select(user_settings).where(user_settings.c.telegram_id == telegram_id)
            if not conn.execute(query).fetchone():
                logger.debug(f"Пользователь {telegram_id} не найден, создаём новую запись")
                conn.execute(insert(user_settings).values(telegram_id=telegram_id, subscribed=False))

            # Формируем данные для обновления
            updates = {}
            if subscribed is not None:
                updates['subscribed'] = subscribed
            updates['vacation_start'] = vacation_start
            updates['vacation_end'] = vacation_end
            if arrival_notification_times is not None:
                updates['arrival_notification_times'] = json.dumps(arrival_notification_times)
            if departure_notification_times is not None:
                updates['departure_notification_times'] = json.dumps(departure_notification_times)

            query = update(user_settings).where(user_settings.c.telegram_id == telegram_id).values(**updates)
            conn.execute(query)
            conn.commit()
            logger.debug(f"Настройки пользователя {telegram_id} обновлены: {updates}")
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при обновлении настроек пользователя {telegram_id}: {e}")
        raise

async def button_handler(update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает нажатия на кнопки меню."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    telegram_id = user.id
    action = query.data

    with engine.connect() as connection:
        if action == 'toggle_subscription':
            sql_query = text("UPDATE user_settings SET subscribed = NOT subscribed WHERE telegram_id = :telegram_id RETURNING subscribed")
            result = connection.execute(sql_query, {"telegram_id": telegram_id}).fetchone()
            connection.commit()
            status = "подписан" if result[0] else "отписан"
            await query.message.reply_text(f"Статус подписки изменён: ты теперь {status} на рассылку.")

        elif action == 'set_vacation':
            await query.message.reply_text("Введи дату начала отпуска в формате ДД-ММ-ГГГГ (например, 01-01-2025):")
            return INPUT_VACATION_START

        elif action == 'clear_vacation':
            sql_query = text("UPDATE user_settings SET vacation_start = NULL, vacation_end = NULL WHERE telegram_id = :telegram_id")
            connection.execute(sql_query, {"telegram_id": telegram_id})
            connection.commit()
            await query.message.reply_text("Даты отпуска удалены.")

        elif action == 'add_arrival_notification_time':
            sql_query = text("SELECT arrival_notification_times FROM user_settings WHERE telegram_id = :telegram_id")
            result = connection.execute(sql_query, {"telegram_id": telegram_id}).mappings().fetchone()
            times = json.loads(result['arrival_notification_times'])
            if len(times) >= 10:
                await query.message.reply_text("Достигнуто максимальное количество оповещений о приходе (10). Удали одно из существующих.")
                return ConversationHandler.END
            await query.message.reply_text("Введи время оповещения о приходе в формате ЧЧ:ММ (например, 09:00):")
            return INPUT_ARRIVAL_NOTIFICATION_TIME

        elif action == 'add_departure_notification_time':
            sql_query = text("SELECT departure_notification_times FROM user_settings WHERE telegram_id = :telegram_id")
            result = connection.execute(sql_query, {"telegram_id": telegram_id}).mappings().fetchone()
            times = json.loads(result['departure_notification_times'])
            if len(times) >= 10:
                await query.message.reply_text("Достигнуто максимальное количество оповещений об уходе (10). Удали одно из существующих.")
                return ConversationHandler.END
            await query.message.reply_text("Введи время оповещения об уходе в формате ЧЧ:ММ (например, 18:00):")
            return INPUT_DEPARTURE_NOTIFICATION_TIME

        elif action == 'remove_arrival_notification_time':
            sql_query = text("SELECT arrival_notification_times FROM user_settings WHERE telegram_id = :telegram_id")
            result = connection.execute(sql_query, {"telegram_id": telegram_id}).mappings().fetchone()
            times = json.loads(result['arrival_notification_times'])
            if not times:
                await query.message.reply_text("Список оповещений о приходе пуст.")
                return ConversationHandler.END
            keyboard = [[InlineKeyboardButton(time, callback_data=f"remove_arrival_time_{time}")] for time in times]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Выбери время оповещения о приходе для удаления:", reply_markup=reply_markup)
            return ConversationHandler.END

        elif action == 'remove_departure_notification_time':
            sql_query = text("SELECT departure_notification_times FROM user_settings WHERE telegram_id = :telegram_id")
            result = connection.execute(sql_query, {"telegram_id": telegram_id}).mappings().fetchone()
            times = json.loads(result['departure_notification_times'])
            if not times:
                await query.message.reply_text("Список оповещений об уходе пуст.")
                return ConversationHandler.END
            keyboard = [[InlineKeyboardButton(time, callback_data=f"remove_departure_time_{time}")] for time in times]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Выбери время оповещения об уходе для удаления:", reply_markup=reply_markup)
            return ConversationHandler.END

        elif action.startswith('remove_arrival_time_'):
            time_to_remove = action[len('remove_arrival_time_'):]
            sql_query = text("SELECT arrival_notification_times FROM user_settings WHERE telegram_id = :telegram_id")
            result = connection.execute(sql_query, {"telegram_id": telegram_id}).mappings().fetchone()
            times = json.loads(result['arrival_notification_times'])
            if time_to_remove in times:
                times.remove(time_to_remove)
                sql_query_update = text("UPDATE user_settings SET arrival_notification_times = :times WHERE telegram_id = :telegram_id")
                connection.execute(sql_query_update, {"times": json.dumps(times), "telegram_id": telegram_id})
                connection.commit()
                await query.message.reply_text(f"Время оповещения о приходе {time_to_remove} удалено.")

        elif action.startswith('remove_departure_time_'):
            time_to_remove = action[len('remove_departure_time_'):]
            sql_query = text("SELECT departure_notification_times FROM user_settings WHERE telegram_id = :telegram_id")
            result = connection.execute(sql_query, {"telegram_id": telegram_id}).mappings().fetchone()
            times = json.loads(result['departure_notification_times'])
            if time_to_remove in times:
                times.remove(time_to_remove)
                sql_query_update = text("UPDATE user_settings SET departure_notification_times = :times WHERE telegram_id = :telegram_id")
                connection.execute(sql_query_update, {"times": json.dumps(times), "telegram_id": telegram_id})
                connection.commit()
                await query.message.reply_text(f"Время оповещения об уходе {time_to_remove} удалено.")

    return ConversationHandler.END

async def set_vacation_start(update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает введённую дату начала отпуска."""
    user = update.effective_user
    telegram_id = user.id
    vacation_start = update.message.text

    try:
        datetime.strptime(vacation_start, '%d-%m-%Y')
    except ValueError:
        await update.message.reply_text("Неверный формат даты. Используй ДД-ММ-ГГГГ (например, 01-01-2025).")
        return INPUT_VACATION_START

    context.user_data['vacation_start'] = vacation_start
    await update.message.reply_text("Введи дату окончания отпуска в формате ДД-ММ-ГГГГ (например, 01-01-2025):")
    return INPUT_VACATION_END

async def set_vacation_end(update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает введённую дату окончания отпуска и сохраняет её."""
    user = update.effective_user
    telegram_id = user.id
    vacation_end = update.message.text

    try:
        datetime.strptime(vacation_end, '%d-%m-%Y')
    except ValueError:
        await update.message.reply_text("Неверный формат даты. Используй ДД-ММ-ГГГГ (например, 01-01-2025).")
        return INPUT_VACATION_END

    vacation_start = context.user_data.get('vacation_start')

    with engine.connect() as connection:
        sql_query = text("""
            UPDATE user_settings
            SET vacation_start = :vacation_start, vacation_end = :vacation_end
            WHERE telegram_id = :telegram_id
        """)
        connection.execute(sql_query, {"vacation_start": vacation_start, "vacation_end": vacation_end, "telegram_id": telegram_id})
        connection.commit()

    await update.message.reply_text(f"Даты отпуска установлены: с {vacation_start} по {vacation_end}.")
    return ConversationHandler.END

async def add_arrival_notification_time(update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Добавляет новое время оповещения о приходе."""
    user = update.effective_user
    telegram_id = user.id
    time_input = update.message.text

    try:
        datetime.strptime(time_input, '%H:%M')
    except ValueError:
        await update.message.reply_text("Неверный формат времени. Используй ЧЧ:ММ (например, 09:00).")
        return INPUT_ARRIVAL_NOTIFICATION_TIME

    with engine.connect() as connection:
        sql_query = text("SELECT arrival_notification_times FROM user_settings WHERE telegram_id = :telegram_id")
        result = connection.execute(sql_query, {"telegram_id": telegram_id}).mappings().fetchone()
        times = json.loads(result['arrival_notification_times'])
        if time_input in times:
            await update.message.reply_text("Это время оповещения о приходе уже добавлено.")
            return ConversationHandler.END
        times.append(time_input)
        sql_query_update = text("UPDATE user_settings SET arrival_notification_times = :times WHERE telegram_id = :telegram_id")
        connection.execute(sql_query_update, {"times": json.dumps(times), "telegram_id": telegram_id})
        connection.commit()

    await update.message.reply_text(f"Время оповещения о приходе {time_input} добавлено.")
    return ConversationHandler.END

async def add_departure_notification_time(update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Добавляет новое время оповещения об уходе."""
    user = update.effective_user
    telegram_id = user.id
    time_input = update.message.text

    try:
        datetime.strptime(time_input, '%H:%M')
    except ValueError:
        await update.message.reply_text("Неверный формат времени. Используй ЧЧ:ММ (например, 18:00).")
        return INPUT_DEPARTURE_NOTIFICATION_TIME

    with engine.connect() as connection:
        sql_query = text("SELECT departure_notification_times FROM user_settings WHERE telegram_id = :telegram_id")
        result = connection.execute(sql_query, {"telegram_id": telegram_id}).mappings().fetchone()
        times = json.loads(result['departure_notification_times'])
        if time_input in times:
            await update.message.reply_text("Это время оповещения об уходе уже добавлено.")
            return ConversationHandler.END
        times.append(time_input)
        sql_query_update = text("UPDATE user_settings SET departure_notification_times = :times WHERE telegram_id = :telegram_id")
        connection.execute(sql_query_update, {"times": json.dumps(times), "telegram_id": telegram_id})
        connection.commit()

    await update.message.reply_text(f"Время оповещения об уходе {time_input} добавлено.")
    return ConversationHandler.END