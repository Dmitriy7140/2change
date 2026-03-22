import logging
import calendar
from datetime import datetime, timedelta, time
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
import os


logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s %(funcName)s %(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs.log', mode="w", encoding='utf-8'),
        logging.StreamHandler()
    ]

)

logger = logging.getLogger(__name__)

def day_off():
    """:returns True if it is day off  """

    date_time = datetime.now()
    current_time = date_time.time()
    if (time(20, 1) <= current_time <= time(23, 59)) or (time(0, 0) <= current_time <= time(9, 59)):
        logger.info("Выходной! Нерабочие часы!")
        return True
    if date_time.weekday() == calendar.SUNDAY:
        logger.info("Выходной! Воскресенье!")
        return True

    logger.info("Не выходной, увы!")
    return False#if not day off

def start_scheduler(daily_task):

    scheduler = BackgroundScheduler()

    msk_tz = pytz.timezone('Europe/Moscow')

    # Ежедневно в 10:00 MSK, кроме воскресенья (mon-fri = 1-5)
    scheduler.add_job(
        daily_task,
        'cron',
        day_of_week='mon-sat',
        hour=10,
        minute=1,
        timezone=msk_tz
    )
    scheduler.start()





def load_changes():
    """Загружает изменения из changes.txt если файл существует"""
    changes_file = "changes.txt"

    if not os.path.exists(changes_file):
        print("Файл changes.txt не найден")
        return None

    try:
        with open(changes_file, 'r', encoding='utf-8') as f:
            changes = f.read().strip()

        if changes:
            print(f"✅ Загружены изменения из changes.txt:\n{changes}")
            return changes
        else:
            print("Файл changes.txt пустой")
            return None

    except Exception as e:
        print(f"❌ Ошибка чтения changes.txt: {e}")
        return None




