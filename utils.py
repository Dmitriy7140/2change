import logging
import calendar
from datetime import datetime, timedelta, time


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
        return True
    if date_time.weekday() == calendar.SUNDAY:
        return True
    if date_time.weekday() == calendar.SATURDAY:
        next_saturday = date_time + timedelta(days=7)
        if next_saturday.month != date_time.month:
            return True
    return False#if not day off




