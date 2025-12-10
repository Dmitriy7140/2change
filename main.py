from bot_main import bot, qdb, manager_chat_id, send_media
from utils import logger

bot_version="pre-release 0.9"
changes=("✅добавили подробные логи\n"
         "✅починили курсы валют\n"
         "✅интегрировали апи\n"
         "✅добавили сообщение, возникающее когда функция в разработке\n"
         "✅починили все что сломалось, сломали то что работало")
if __name__ == '__main__':
    try:
        logger.info("2change стартует...")

        qdb.update_currency()
        logger.info("Курсики подтянули, запускаемся...")
        bot.send_message(manager_chat_id, text="Калькулятор 2change на связи🤙\n\n"
                                                f"версия: {bot_version}\n\n" + changes, disable_notification=True)

        bot.infinity_polling()
    except KeyboardInterrupt:
        send_media("img/bye.mp4", manager_chat_id, caption="Калькулятор 2change выключается...")