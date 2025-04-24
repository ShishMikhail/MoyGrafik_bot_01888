import logging
import sys
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime
from sqlalchemy import text

# Добавляем корень проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from bot.settings import get_user_settings, update_user_settings
from bot.status_checker import get_attendance, get_attendance_last_10_days
from bot.utils import INPUT_VACATION_START, INPUT_VACATION_END, INPUT_ARRIVAL_NOTIFICATION_TIME, \
    INPUT_DEPARTURE_NOTIFICATION_TIME
from database.db import engine

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler('handlers.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
SET_VACATION_START, SET_VACATION_END, ADD_ARRIVAL_NOTIFICATION, ADD_DEPARTURE_NOTIFICATION = range(INPUT_VACATION_START,
                                                                                                   INPUT_DEPARTURE_NOTIFICATION_TIME + 1)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.debug(f"Получена команда /start от пользователя {user_id}")

    # Создаём кнопки (они будут внизу сообщения)
    keyboard = [
        [InlineKeyboardButton("📩 Подписка на рассылку", callback_data='toggle_subscription')],
        [InlineKeyboardButton("🏖️ Задать даты отпуска", callback_data='set_vacation'),
         InlineKeyboardButton("❌ Удалить даты отпуска", callback_data='clear_vacation')],
        [InlineKeyboardButton("⏰ Добавить время оповещений о приходе", callback_data='add_arrival_notification_time'),
         InlineKeyboardButton("🗑️ Удалить время оповещений о приходе",
                              callback_data='remove_arrival_notification_time')],
        [InlineKeyboardButton("⏰ Добавить время оповещений об уходе", callback_data='add_departure_notification_time'),
         InlineKeyboardButton("🗑️ Удалить время оповещений об уходе",
                              callback_data='remove_departure_notification_time')],
        [InlineKeyboardButton("📅 Посещения за сегодня", callback_data='attendance_today'),
         InlineKeyboardButton("📊 Посещения за 10 дней", callback_data='attendance_10_days')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Проверяем пользователя в базе данных
    with engine.connect() as connection:
        # Ищем employee_id по telegram_id
        query = text("SELECT employee_id FROM user_settings WHERE telegram_id = :telegram_id")
        result = connection.execute(query, {"telegram_id": user_id}).mappings().fetchone()

        if not result:
            # Если пользователь не найден, предлагаем зарегистрироваться
            message = (
                "👋 Привет! Я твой бот для управления графиком работы.\n\n"
                "❌ Кажется, ты ещё не зарегистрирован.\n"
                "Используй команду /register, чтобы начать! 📝"
            )
            await update.message.reply_text(message, reply_markup=reply_markup)
            return ConversationHandler.END

        employee_id = result['employee_id']

        # Ищем имя сотрудника по employee_id
        query = text("SELECT first_name, last_name FROM employees WHERE id = :employee_id")
        employee = connection.execute(query, {"employee_id": employee_id}).mappings().fetchone()

        if not employee:
            # Если сотрудник не найден, используем стандартное приветствие
            message = (
                "👋 Привет! Я твой бот для управления графиком работы.\n\n"
                "❌ Не удалось найти твои данные. Возможно, сотрудник не привязан.\n"
                "Попробуй перерегистрироваться с помощью /register. 📝"
            )
            await update.message.reply_text(message, reply_markup=reply_markup)
            return ConversationHandler.END

        first_name = employee['first_name']
        last_name = employee['last_name']

    # Получаем текущие настройки пользователя
    subscribed, vacation_start, vacation_end, arrival_notification_times, departure_notification_times = get_user_settings(
        user_id)

    # Формируем читаемый текст с смайликами
    subscription_status = "подписан ✅" if subscribed else "не подписан 🚫"
    vacation_text = f"{vacation_start} - {vacation_end}" if vacation_start and vacation_end else "не задан 📅"
    arrival_notifications_text = ', '.join(arrival_notification_times) if arrival_notification_times else "не задано ⏰"
    departure_notifications_text = ', '.join(
        departure_notification_times) if departure_notification_times else "не задано ⏰"

    message = (
        f"👋 Привет, {first_name} {last_name}! Я твой бот для управления графиком работы.\n\n"
        "📋 Твои текущие настройки:\n"
        f"📩 Подписка на рассылку: {subscription_status}\n"
        f"🏖️ Даты отпуска: {vacation_text}\n"
        f"⏰ Время оповещений о приходе: {arrival_notifications_text}\n"
        f"⏰ Время оповещений об уходе: {departure_notifications_text}\n\n"
        "Выбери, что хочешь сделать: 👇"
    )

    await update.message.reply_text(message, reply_markup=reply_markup)
    return ConversationHandler.END


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.debug(f"Получена команда /menu от пользователя {user_id}")

    # Создаём кнопки (они будут внизу сообщения)
    keyboard = [
        [InlineKeyboardButton("📩 Подписка на рассылку", callback_data='toggle_subscription')],
        [InlineKeyboardButton("🏖️ Задать даты отпуска", callback_data='set_vacation'),
         InlineKeyboardButton("❌ Удалить даты отпуска", callback_data='clear_vacation')],
        [InlineKeyboardButton("⏰ Добавить время оповещений о приходе", callback_data='add_arrival_notification_time'),
         InlineKeyboardButton("🗑️ Удалить время оповещений о приходе",
                              callback_data='remove_arrival_notification_time')],
        [InlineKeyboardButton("⏰ Добавить время оповещений об уходе", callback_data='add_departure_notification_time'),
         InlineKeyboardButton("🗑️ Удалить время оповещений об уходе",
                              callback_data='remove_departure_notification_time')],
        [InlineKeyboardButton("📅 Посещения за сегодня", callback_data='attendance_today'),
         InlineKeyboardButton("📊 Посещения за 10 дней", callback_data='attendance_10_days')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Получаем текущие настройки пользователя
    subscribed, vacation_start, vacation_end, arrival_notification_times, departure_notification_times = get_user_settings(
        user_id)

    # Формируем читаемый текст с смайликами
    subscription_status = "подписан ✅" if subscribed else "не подписан 🚫"
    vacation_text = f"{vacation_start} - {vacation_end}" if vacation_start and vacation_end else "не задан 📅"
    arrival_notifications_text = ', '.join(arrival_notification_times) if arrival_notification_times else "не задано ⏰"
    departure_notifications_text = ', '.join(
        departure_notification_times) if departure_notification_times else "не задано ⏰"

    message = (
        "📋 Твоё меню настроек:\n\n"
        f"📩 Подписка на рассылку: {subscription_status}\n"
        f"🏖️ Даты отпуска: {vacation_text}\n"
        f"⏰ Время оповещений о приходе: {arrival_notifications_text}\n"
        f"⏰ Время оповещений об уходе: {departure_notifications_text}\n\n"
        "Выбери действие: 👇"
    )

    await update.message.reply_text(message, reply_markup=reply_markup)
    return ConversationHandler.END


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.debug(f"Получена команда /status от пользователя {user_id}")

    # Получаем текущие настройки пользователя
    subscribed, vacation_start, vacation_end, arrival_notification_times, departure_notification_times = get_user_settings(
        user_id)

    # Формируем читаемый текст с смайликами
    subscription_status = "подписан ✅" if subscribed else "не подписан 🚫"
    vacation_text = f"{vacation_start} - {vacation_end}" if vacation_start and vacation_end else "не задан 📅"
    arrival_notifications_text = ', '.join(arrival_notification_times) if arrival_notification_times else "не задано ⏰"
    departure_notifications_text = ', '.join(
        departure_notification_times) if departure_notification_times else "не задано ⏰"

    message = (
        "📋 Твой текущий статус:\n\n"
        f"📩 Подписка на рассылку: {subscription_status}\n"
        f"🏖️ Даты отпуска: {vacation_text}\n"
        f"⏰ Время оповещений о приходе: {arrival_notifications_text}\n"
        f"⏰ Время оповещений об уходе: {departure_notifications_text}"
    )

    await update.message.reply_text(message)
    return ConversationHandler.END


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    callback_data = query.data
    logger.debug(f"Получен callback-запрос от пользователя {user_id}: callback_data={callback_data}")

    subscribed, vacation_start, vacation_end, arrival_notification_times, departure_notification_times = get_user_settings(
        user_id)

    if callback_data == 'toggle_subscription':
        new_subscribed = not subscribed
        update_user_settings(user_id, subscribed=new_subscribed)
        status = "подписан ✅" if new_subscribed else "отписан 🚫"
        await query.message.reply_text(f"📩 Подписка на рассылку: {status}")

    elif callback_data == 'set_vacation':
        await query.message.reply_text("📅 Введи дату начала отпуска в формате ДД-ММ-ГГГГ (например, 01-01-2025):")
        return SET_VACATION_START

    elif callback_data == 'clear_vacation':
        logger.debug(f"Попытка удалить даты отпуска для пользователя {user_id}")
        if not vacation_start and not vacation_end:
            await query.message.reply_text("🏖️ У тебя нет установленных дат отпуска! 😕")
            return ConversationHandler.END
        update_user_settings(user_id, vacation_start=None, vacation_end=None)
        logger.debug(f"Даты отпуска для пользователя {user_id} сброшены")

        # Получаем обновленные настройки
        subscribed, vacation_start, vacation_end, arrival_notification_times, departure_notification_times = get_user_settings(
            user_id)
        subscription_status = "подписан ✅" if subscribed else "не подписан 🚫"
        vacation_text = f"{vacation_start} - {vacation_end}" if vacation_start and vacation_end else "не задан 📅"
        arrival_notifications_text = ', '.join(
            arrival_notification_times) if arrival_notification_times else "не задано ⏰"
        departure_notifications_text = ', '.join(
            departure_notification_times) if departure_notification_times else "не задано ⏰"

        message = (
            "🏖️ Даты отпуска успешно удалены! ✅\n\n"
            "📋 Твои текущие настройки:\n"
            f"📩 Подписка на рассылку: {subscription_status}\n"
            f"🏖️ Даты отпуска: {vacation_text}\n"
            f"⏰ Время оповещений о приходе: {arrival_notifications_text}\n"
            f"⏰ Время оповещений об уходе: {departure_notifications_text}"
        )
        await query.message.reply_text(message)

    elif callback_data == 'add_arrival_notification_time':
        if len(arrival_notification_times) >= 10:
            await query.message.reply_text(
                "⏰ Достигнуто максимальное количество оповещений о приходе (10). Удали одно из существующих! 🗑️")
            return ConversationHandler.END
        await query.message.reply_text("⏰ Введи время оповещения о приходе в формате ЧЧ:ММ (например, 09:00):")
        return ADD_ARRIVAL_NOTIFICATION

    elif callback_data == 'add_departure_notification_time':
        if len(departure_notification_times) >= 10:
            await query.message.reply_text(
                "⏰ Достигнуто максимальное количество оповещений об уходе (10). Удали одно из существующих! 🗑️")
            return ConversationHandler.END
        await query.message.reply_text("⏰ Введи время оповещения об уходе в формате ЧЧ:ММ (например, 18:00):")
        return ADD_DEPARTURE_NOTIFICATION

    elif callback_data == 'remove_arrival_notification_time':
        if not arrival_notification_times:
            await query.message.reply_text("⏰ У тебя нет установленных времен оповещений о приходе! 😕")
            return ConversationHandler.END
        keyboard = [[InlineKeyboardButton(f"{time} 🗑️", callback_data=f"remove_arrival_time_{time}")] for time in
                    arrival_notification_times]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("⏰ Выбери время оповещения о приходе для удаления: 👇", reply_markup=reply_markup)

    elif callback_data == 'remove_departure_notification_time':
        if not departure_notification_times:
            await query.message.reply_text("⏰ У тебя нет установленных времен оповещений об уходе! 😕")
            return ConversationHandler.END
        keyboard = [[InlineKeyboardButton(f"{time} 🗑️", callback_data=f"remove_departure_time_{time}")] for time in
                    departure_notification_times]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("⏰ Выбери время оповещения об уходе для удаления: 👇", reply_markup=reply_markup)

    elif callback_data.startswith('remove_arrival_time_'):
        time_to_remove = callback_data[len('remove_arrival_time_'):]
        if time_to_remove in arrival_notification_times:
            arrival_notification_times.remove(time_to_remove)
            update_user_settings(user_id, arrival_notification_times=arrival_notification_times)
            await query.message.reply_text(f"⏰ Время оповещения о приходе {time_to_remove} удалено! ✅")
        else:
            await query.message.reply_text("⏰ Это время уже удалено! 😕")

    elif callback_data.startswith('remove_departure_time_'):
        time_to_remove = callback_data[len('remove_departure_time_'):]
        if time_to_remove in departure_notification_times:
            departure_notification_times.remove(time_to_remove)
            update_user_settings(user_id, departure_notification_times=departure_notification_times)
            await query.message.reply_text(f"⏰ Время оповещения об уходе {time_to_remove} удалено! ✅")
        else:
            await query.message.reply_text("⏰ Это время уже удалено! 😕")

    elif callback_data == 'attendance_today':
        today = datetime.now().strftime('%Y-%m-%d')
        status = get_attendance(user_id, today)
        await query.message.reply_text(f"📅 Посещения за сегодня ({today}):\n{status}")

    elif callback_data == 'attendance_10_days':
        today = datetime.now().strftime('%Y-%m-%d')
        records = get_attendance_last_10_days(user_id, today)
        if not records:
            await query.message.reply_text("📊 Нет данных за последние 10 дней! 😕")
            return
        response = "📊 Посещения за последние 10 дней:\n"
        for date, status in records:
            response += f"{date}: {status}\n"
        await query.message.reply_text(response)

    return ConversationHandler.END


async def set_vacation_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    try:
        vacation_start = datetime.strptime(text, '%d-%m-%Y').strftime('%Y-%m-%d')
        context.user_data['vacation_start'] = vacation_start
        await update.message.reply_text("📅 Введи дату окончания отпуска в формате ДД-ММ-ГГГГ (например, 01-01-2025):")
        return SET_VACATION_END
    except ValueError:
        await update.message.reply_text("❌ Неверный формат даты. Попробуй еще раз (ДД-ММ-ГГГГ):")
        return SET_VACATION_START


async def set_vacation_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    try:
        vacation_end = datetime.strptime(text, '%d-%m-%Y').strftime('%Y-%m-%d')
        vacation_start = context.user_data.get('vacation_start')
        if not vacation_start:
            await update.message.reply_text("❌ Произошла ошибка. Начни заново. 😕")
            return ConversationHandler.END
        update_user_settings(user_id, vacation_start=vacation_start, vacation_end=vacation_end)
        await update.message.reply_text(f"🏖️ Даты отпуска установлены: {vacation_start} - {vacation_end} ✅")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("❌ Неверный формат даты. Попробуй еще раз (ДД-ММ-ГГГГ):")
        return SET_VACATION_END


async def add_arrival_notification_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    try:
        datetime.strptime(text, '%H:%M')  # Проверка формата
        subscribed, vacation_start, vacation_end, arrival_notification_times, departure_notification_times = get_user_settings(
            user_id)
        if text not in arrival_notification_times:
            arrival_notification_times.append(text)
            update_user_settings(user_id, arrival_notification_times=arrival_notification_times)
            await update.message.reply_text(f"⏰ Время оповещения о приходе {text} добавлено! ✅")
        else:
            await update.message.reply_text(f"⏰ Время оповещения о приходе {text} уже есть! 😕")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("❌ Неверный формат времени. Попробуй еще раз (ЧЧ:ММ):")
        return ADD_ARRIVAL_NOTIFICATION


async def add_departure_notification_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    try:
        datetime.strptime(text, '%H:%M')  # Проверка формата
        subscribed, vacation_start, vacation_end, arrival_notification_times, departure_notification_times = get_user_settings(
            user_id)
        if text not in departure_notification_times:
            departure_notification_times.append(text)
            update_user_settings(user_id, departure_notification_times=departure_notification_times)
            await update.message.reply_text(f"⏰ Время оповещения об уходе {text} добавлено! ✅")
        else:
            await update.message.reply_text(f"⏰ Время оповещения об уходе {text} уже есть! 😕")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("❌ Неверный формат времени. Попробуй еще раз (ЧЧ:ММ):")
        return ADD_DEPARTURE_NOTIFICATION