import asyncio
import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from bot.scheduler import setup_scheduler
from bot.handlers import (
    start, menu, status, callback_handler, set_vacation_start, set_vacation_end,
    add_arrival_notification_time, add_departure_notification_time
)
from bot.settings import button_handler, set_vacation_start as settings_set_vacation_start, set_vacation_end as settings_set_vacation_end
from bot.settings import add_arrival_notification_time as settings_add_arrival_notification_time
from bot.settings import add_departure_notification_time as settings_add_departure_notification_time
from bot.utils import (
    INPUT_VACATION_START, INPUT_VACATION_END, INPUT_ARRIVAL_NOTIFICATION_TIME, INPUT_DEPARTURE_NOTIFICATION_TIME
)

# Путь к директории текущего файла (где находится main.py)
current_directory = os.path.dirname(__file__)

# Путь к файлу TG_BOT.txt в той же директории
token_file_path = os.path.join(current_directory, 'TG_TOKEN.txt')

# Чтение токена из файла
with open(token_file_path, 'r') as token_file:
    TELEGRAM_TOKEN = token_file.read().strip()

# Создаём приложение
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Определяем ConversationHandler для обработки пошагового ввода
conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback_handler, pattern='^(toggle_subscription|set_vacation|clear_vacation|add_arrival_notification_time|add_departure_notification_time|remove_arrival_notification_time|remove_departure_notification_time|attendance_today|attendance_10_days)$'),
        CallbackQueryHandler(button_handler, pattern='^(toggle_subscription|set_vacation|clear_vacation|add_arrival_notification_time|add_departure_notification_time|remove_arrival_notification_time|remove_departure_notification_time)$'),
    ],
    states={
        INPUT_VACATION_START: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, set_vacation_start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, settings_set_vacation_start),
        ],
        INPUT_VACATION_END: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, set_vacation_end),
            MessageHandler(filters.TEXT & ~filters.COMMAND, settings_set_vacation_end),
        ],
        INPUT_ARRIVAL_NOTIFICATION_TIME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_arrival_notification_time),
            MessageHandler(filters.TEXT & ~filters.COMMAND, settings_add_arrival_notification_time),
        ],
        INPUT_DEPARTURE_NOTIFICATION_TIME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_departure_notification_time),
            MessageHandler(filters.TEXT & ~filters.COMMAND, settings_add_departure_notification_time),
        ],
    },
    fallbacks=[],
)

# Добавляем обработчики
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("status", status))
app.add_handler(conv_handler)

# Настраиваем планировщик задач
setup_scheduler(app)

# Запускаем бота
if __name__ == "__main__":
    print("Бот запущен...")
    app.run_polling()