
from bot_main import bot,manager_chat_id, send_media

from utils import logger

bot_version="beta 1.4"
changes="Добавлено подтверждение заявок!"
if __name__ == '__main__':
    try:
        logger.info("2change стартует...")



        logger.info("Курсики подтянули, запускаемся...")
        bot.send_message(manager_chat_id, text="Калькулятор 2change на связи🤙\n\n"
                                                f"версия: {bot_version}\n\n" + changes, disable_notification=True)


        bot.infinity_polling()
    except KeyboardInterrupt:
        send_media("img/bye.mp4", manager_chat_id, caption="Калькулятор 2change выключается...")