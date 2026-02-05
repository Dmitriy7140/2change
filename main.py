
from bot_main import bot,manager_chat_id, send_media, handle_queue

from utils import logger, start_scheduler, load_changes
import threading

changes = load_changes()
if __name__ == '__main__':
    try:
        logger.info("2change стартует...")





        if changes:
            bot.send_message(
                manager_chat_id,
                f"📋 <b>Что нового в боте:</b>\n\n{changes}",
                parse_mode="HTML"
            )
        else:
            pass
        scheduler_thread = threading.Thread(target=start_scheduler, args=(handle_queue,), daemon=True)
        scheduler_thread.start()


        bot.infinity_polling()
    except KeyboardInterrupt:
        send_media("img/bye.mp4", manager_chat_id, caption="Калькулятор 2change выключается...")