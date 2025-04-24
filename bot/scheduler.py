import logging
from telegram.ext import Application
from bot.notifications import check_absences

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def setup_scheduler(app: Application) -> None:
    """
    Настраивает планировщик задач для периодической проверки отсутствия отметок.
    """
    logger.info("Настройка планировщика задач...")

    # Добавляем задачу, которая будет выполняться каждую минуту
    app.job_queue.run_repeating(check_absences, interval=60, first=0)

    logger.info("Планировщик задач настроен и запущен.")