import sys
import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import text, select, update, insert
from sqlalchemy.exc import SQLAlchemyError
import logging

# Добавляем корень проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from database.db import engine, user_settings, presence_report
from bot.utils import VLADIVOSTOK_TZ

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

def add_attendance(employee_id, date, start_time=None, end_time=None, is_night_shift=False):
    """
    Добавление записи о посещении в таблицу presence_report.
    """
    try:
        with engine.connect() as conn:
            # Проверяем, существует ли запись
            query = select(presence_report).where(
                presence_report.c.employee_id == employee_id,
                presence_report.c.date == date
            )
            existing = conn.execute(query).mappings().fetchone()

            if existing:
                # Обновляем существующую запись
                updates = {
                    'start_time': start_time if start_time else existing['start_time'],
                    'end_time': end_time if end_time else existing['end_time'],
                    'is_night_shift': is_night_shift
                }
                query = update(presence_report).where(
                    presence_report.c.employee_id == employee_id,
                    presence_report.c.date == date
                ).values(**updates)
            else:
                # Создаём новую запись
                query = insert(presence_report).values(
                    employee_id=employee_id,
                    date=date,
                    start_time=start_time,
                    end_time=end_time,
                    is_night_shift=is_night_shift,
                    original_estimate=0,  # Можно настроить
                    real_estimate=0,      # Можно настроить
                    is_red=False
                )
            conn.execute(query)
            conn.commit()
            logger.debug(f"Запись о посещении добавлена/обновлена для employee_id {employee_id} на дату {date}")
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении записи о посещении: {e}")
        raise

def get_attendance(telegram_id, date):
    """
    Получение данных о посещении за конкретный день.
    Возвращает строку с информацией о посещении.
    """
    try:
        with engine.connect() as conn:
            # Находим employee_id по telegram_id
            query = select(user_settings.c.employee_id).where(user_settings.c.telegram_id == telegram_id)
            result = conn.execute(query).mappings().fetchone()
            if not result:
                return "Пользователь не найден в настройках."

            employee_id = result['employee_id']
            query = select(presence_report).where(
                presence_report.c.employee_id == employee_id,
                presence_report.c.date == date
            )
            record = conn.execute(query).mappings().fetchone()
            if record:
                start_time = record['start_time'] or "не указано"
                end_time = record['end_time'] or "не указано"
                return f"Начало: {start_time}, Конец: {end_time}, Ночная смена: {'Да' if record['is_night_shift'] else 'Нет'}"
            return "Нет данных о посещении за этот день."
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении данных о посещении для {telegram_id} на дату {date}: {e}")
        return "Ошибка при получении данных."

def get_attendance_last_10_days(telegram_id, end_date):
    """
    Получение данных о посещениях за последние 10 дней.
    Возвращает список записей.
    """
    try:
        with engine.connect() as conn:
            # Находим employee_id по telegram_id
            query = select(user_settings.c.employee_id).where(user_settings.c.telegram_id == telegram_id)
            result = conn.execute(query).mappings().fetchone()
            if not result:
                return []

            employee_id = result['employee_id']
            end = datetime.strptime(end_date, '%Y-%m-%d')
            start = end - timedelta(days=9)

            query = select(presence_report).where(
                presence_report.c.employee_id == employee_id,
                presence_report.c.date.between(start.strftime('%Y-%m-%d'), end_date)
            )
            records = conn.execute(query).mappings().fetchall()
            return [(record['date'], f"Начало: {record['start_time'] or 'не указано'}, Конец: {record['end_time'] or 'не указано'}") for record in records]
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении данных о посещениях за 10 дней для {telegram_id}: {e}")
        return []

async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Проверяет текущий статус пользователя (приход/уход)."""
    user = update.effective_user
    telegram_id = user.id

    with engine.connect() as connection:
        # Получаем employee_id пользователя
        query = text("SELECT employee_id FROM user_settings WHERE telegram_id = :telegram_id")
        result = connection.execute(query, {"telegram_id": telegram_id}).mappings().fetchone()

        if not result:
            await update.message.reply_text("Ты не зарегистрирован. Используй /register для регистрации.")
            return

        employee_id = result['employee_id']

        # Находим последнюю запись в presence_report
        query = text("""
            SELECT date, start_time, end_time
            FROM presence_report
            WHERE employee_id = :employee_id
            ORDER BY date DESC, start_time DESC
            LIMIT 1
        """)
        result = connection.execute(query, {"employee_id": employee_id}).mappings().fetchone()

        if not result:
            await update.message.reply_text("У тебя нет записей о присутствии.")
            return

        date = result['date']
        start_time = result['start_time']
        end_time = result['end_time']
        status = "приход" if start_time and not end_time else "уход"
        time = start_time if status == "приход" else end_time

        await update.message.reply_text(
            f"Твой текущий статус: {status}\n"
            f"Дата: {date}\n"
            f"Время: {time}"
        )

async def attendance_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает статистику посещений за последние 10 дней."""
    user = update.effective_user
    telegram_id = user.id

    with engine.connect() as connection:
        # Получаем employee_id пользователя
        query = text("SELECT employee_id FROM user_settings WHERE telegram_id = :telegram_id")
        result = connection.execute(query, {"telegram_id": telegram_id}).mappings().fetchone()

        if not result:
            await update.message.reply_text("Ты не зарегистрирован. Используй /register для регистрации.")
            return

        employee_id = result['employee_id']

        # Определяем диапазон дат (последние 10 дней)
        end_date = datetime.now(VLADIVOSTOK_TZ).strftime('%Y-%m-%d')
        start_date = (datetime.now(VLADIVOSTOK_TZ) - timedelta(days=9)).strftime('%Y-%m-%d')

        # Получаем записи за последние 10 дней
        query = text("""
            SELECT date, start_time, end_time, is_red
            FROM presence_report
            WHERE employee_id = :employee_id
            AND date BETWEEN :start_date AND :end_date
            ORDER BY date
        """)
        results = connection.execute(query, {"employee_id": employee_id, "start_date": start_date, "end_date": end_date}).mappings().fetchall()

        if not results:
            await update.message.reply_text("Нет записей о посещениях за последние 10 дней.")
            return

        # Формируем статистику
        stats = []
        for record in results:
            date = record['date']
            start_time = record['start_time']
            end_time = record['end_time']
            is_red = record['is_red']
            status = "Приход" if start_time else "Уход"
            time = start_time if start_time else end_time
            red_status = " (просрочено)" if is_red else ""
            stats.append(f"{date}: {status} в {time}{red_status}")

        await update.message.reply_text(
            "Статистика посещений за последние 10 дней:\n" + "\n".join(stats)
        )