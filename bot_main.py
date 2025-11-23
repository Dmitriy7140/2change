import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from utils import logger

#глобали


admin_id = 57713855


class MyExceptionHandler(telebot.ExceptionHandler):

    def handle(self, exception):

        message = f"Ошибка в боте: {exception}"
        logger.error(message, exc_info=True)
        # Здесь можно добавить логирование ошибки, например через logger
        bot.send_message(admin_id, message)
        return True

bot = telebot.TeleBot( "8559812575:AAFducMZ0rp9WKCbo_pv8yyhkMAG8Drz6m8", exception_handler=MyExceptionHandler())

@bot.message_handler(commands=['start'])
def handle_start(message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1= InlineKeyboardButton( "🇹🇷 Турция", callback_data="turkey_menu")
    button2 = InlineKeyboardButton("🇹🇭 Тайланд", callback_data="thai_menu")
    keyboard.row(button1, button2)

    keyboard.add(InlineKeyboardButton("🇷🇺 Россия", callback_data="rf_menu"))
    keyboard.add(InlineKeyboardButton("🛡 Гарантии и отзывы", callback_data="comment_menu"))
    keyboard.add(InlineKeyboardButton("💳 Зарубежная карта", callback_data="card_menu"))
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    msg = (f'Здравствуйте, <a href="tg://user?id={user_id}">👋 {first_name}</a>!\n'
              f'Я — Ботя, помощник сервиса 2Change — ваш надежный финансовый партнер в поездках за границу: Турция, Тайиланд, Корея, ОАЭ и др (20+ стран)\n\n'
                f"Обмен, переводы, eSIM, зарубежные карты и поддержка — всё быстро, удобно и с заботой.\n\n"

                f"✅ Я помогу вам:\n"
                f"▪️ Рассчитать сумму обмена\n"
                f"▪️ Узнать актуальный курс\n"
                f"▪️ Подключить eSIM\n"
                f"▪️ Оставить заявку на обмен\n\n"

                f"🕒 Пн–Сб 10:00-20:00 (по Мск)\n"
                f"❗️@ALEXANDRA_2CHANGE - <i>единственный менеджер 2Change</i> — /manager")
    with open("img/intro.mp4", "rb") as video:
        bot.send_video(message.chat.id, video, caption=msg,reply_markup=keyboard, parse_mode="HTML")


