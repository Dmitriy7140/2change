
from bot_main import bot, queue_service, sender_service, anal_sheets

from utils import logger, start_scheduler
import threading


if __name__ == '__main__':

    logger.info("2change стартует...")
    scheduler_thread = threading.Thread(target=start_scheduler,
                                        args=(queue_service, sender_service, anal_sheets), daemon=True)
    scheduler_thread.start()

    bot.infinity_polling()
