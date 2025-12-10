from bot_main import bot, qdb

if __name__ == '__main__':
    qdb.update_currency()
    bot.infinity_polling()