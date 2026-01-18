
from bot_main import bot,manager_chat_id, send_media, handle_queue

from utils import logger, start_scheduler
import threading

bot_version="1.6.0"
changes=("🌟Добавлено подтверждение заявок!\n"
         "🌟Бот автоматически запрашивает подтверждение каждое утро!\n"
         "")
if __name__ == '__main__':
    try:
        logger.info("2change стартует...")




        bot.send_message(manager_chat_id, text="Калькулятор 2change на связи🤙\n\n"
                                                f"версия: {bot_version}\n\n" + changes, disable_notification=True)
        scheduler_thread = threading.Thread(target=start_scheduler, args=(handle_queue,), daemon=True)
        scheduler_thread.start()


        bot.infinity_polling()
    except KeyboardInterrupt:
        send_media("img/bye.mp4", manager_chat_id, caption="Калькулятор 2change выключается...")