
from bot_main import bot, handle_queue

from utils import logger, start_scheduler
import threading


if __name__ == '__main__':

    logger.info("2change стартует...")






    scheduler_thread = threading.Thread(target=start_scheduler,
                                        args=(handle_queue,), daemon=True)
    scheduler_thread.start()


    bot.infinity_polling()
