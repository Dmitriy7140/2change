import logging
import calendar
from datetime import datetime, time
import pytz
from apscheduler.schedulers.background import BackgroundScheduler



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












