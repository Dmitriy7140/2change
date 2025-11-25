import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import logger

#глобали
img_cache={}

admin_id = 57713855
manager_chat_id = ""
tr_chat_username = "@asas_magov"


class MyExceptionHandler(telebot.ExceptionHandler):

    def handle(self, exception):

        message = f"Ошибка в боте: {exception}"
        logger.error(message, exc_info=True)
        # Здесь можно добавить логирование ошибки, например через logger
        bot.send_message(admin_id, message)
        return True

bot = telebot.TeleBot( "8559812575:AAFducMZ0rp9WKCbo_pv8yyhkMAG8Drz6m8", exception_handler=MyExceptionHandler())


def check_subscribtion(user_id, country):
    if country == 1: #tr

        chat_member = bot.get_chat_member(tr_chat_username, user_id)

        if chat_member.status in ("creator", "administrator", "member"):

            return True
        else:

            return False

@bot.message_handler(commands=['start'])
def handle_start(message, not_first:bool=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1= InlineKeyboardButton( "🇹🇷 Турция", callback_data="tr_menu")
    button2 = InlineKeyboardButton("🇹🇭 Тайланд", callback_data="thai_menu")
    keyboard.row(button1, button2)

    keyboard.add(InlineKeyboardButton("🇷🇺 Россия", callback_data="rf_menu"))
    keyboard.add(InlineKeyboardButton("🛡 Гарантии и отзывы", callback_data="comment_menu"))
    keyboard.add(InlineKeyboardButton("💳 Зарубежная карта", callback_data="card_menu"))
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    video_path = "img/intro.mp4"
    if not_first:
        msg = (f'Чем еще могу помочь?\n'
               f'Напомню, я — Ботя, помощник сервиса 2Change — ваш надежный финансовый партнер в поездках за границу: Турция, Тайиланд, Корея, ОАЭ и др (20+ стран)\n\n'
               f"Обмен, переводы, eSIM, зарубежные карты и поддержка — всё быстро, удобно и с заботой.\n\n"

               f"✅ Я помогу вам:\n"
               f"▪️ Рассчитать сумму обмена\n"
               f"▪️ Узнать актуальный курс\n"
               f"▪️ Подключить eSIM\n"
               f"▪️ Оставить заявку на обмен\n\n"

               f"🕒 Пн–Сб 10:00-20:00 (по Мск)\n"
               f"❗️@ALEXANDRA_2CHANGE - <i>единственный менеджер 2Change</i> — /manager")

    else:
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
    if video_path in img_cache:
        bot.send_video(message.chat.id, img_cache[video_path], caption=msg, reply_markup=keyboard, parse_mode="HTML")

    else:
        with open(video_path, "rb") as video:
            sent = bot.send_video(message.chat.id, video, caption=msg,reply_markup=keyboard, parse_mode="HTML")
            img_cache[video_path] = sent.video.file_id

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    if call.data=="tr_menu":
        if check_subscribtion(user_id, 1):
            bot.send_message(chat_id, "салам армян")
        else:
            bot.send_message(chat_id,"<i>Для работы с ботом\n"
                            "Подпишитесь на 👉  <a href='https://t.me/turkey_2change'>чат 2Change</a></i>",
                            parse_mode="HTML")
    if call.data=="comment_menu":
        msg = ('<b>Мы дорожим нашей репутацией, благодаря этому наш сервис работает уже 3 года.⭐️\n\n'
               '✅Про нас писали в газете <a href="https://t.me/review_2change/394">«Один из популярных сервисов обмена Турции»</a>\n'
               '✅Рекомендация сервиса <a href="https://journal.tinkoff.ru/kak-pomeniat-dengi-v-turtsii-v-2024/https://journal.tinkoff.ru/kak-pomeniat-dengi-v-turtsii-v-2024/">2Сhange в Тинькоф Журнале</a>\n'
               '✅Рекомендация на <a href="https://vc.ru/u/2800953-nikita-ryabkov/1012718-kak-obmenyat-dengi-v-turcii-vse-rabochie-sposoby-v-2024-godu?ysclid=m2men5tdyu815248852">VC.RU</a>\n'
               '✅Популярный <a href="https://t.me/brizhak_ilia/1703">тревел-блоггер Илья Брижак о нас</a>\n'
               '✅Бизнес-школа Бизнес Факт и бизнес-тренер №1 <a href="https://t.me/review_2pay/22">Алексей Максимченков рекомендуют наш сервис</a>\n'
               '✅Официальный партнер проекта <a href="http://t.me/slavianskiy_forum">«Эмигрант 360»</a>\n'
               '✅Про нас опубликовали видео <a href="https://www.youtube.com/watch?v=L1zMcBJQDjI">на популярном YouTube канале про Турцию</a>\n'
               '✅Отзывы по обмену валют - @review_2change\n'
               '✅Отзывы по оплате зарубежных сервисов и денежных переводов, открытия карт - @review_2pay\n\n</b>'
               'Смотрите больше отзывов в группе или оставьте свой')
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("Смотреть отзывы🔎", url="https://t.me/review_2change"))
        keyboard.add(InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
        bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)
    if call.data=="main_menu":
        handle_start(call.message, True)

    if call.data=="card_menu":
        if check_subscribtion(user_id, 1):
            photo_path = "img/card.jpg"
            msg =("💳 Оформим зарубежную карту Visa за 5 минут!\n\n"
                 "🌍 Оплата и снятие наличных в Турции и по всему миру\n"
                 "💳 Моментальное пополнение с российской карты\n"
                 "⚡️ Онлайн-регистрация за 5 минут\n"
                 "🇷🇺 Приложение на русском языке (IOS/Android)\n"
                 "🛫 Доставка по РФ\n\n"
                
                 "Подробнее 👉<a href='https://telegra.ph/Karty-VisaMastercard-ot-2ChangePay-10-15'> в статье </a>\n\n"
                
                 "⬇️ Оставьте заявку или напишите менеджеру @ALEXANDRA_2CHANGE")
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("Оставить заявку✅", callback_data="tr_card_request"))
            keyboard.add(InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
            if photo_path in img_cache:
                bot.send_photo(chat_id, img_cache[photo_path], caption=msg, reply_markup=keyboard,
                               parse_mode="HTML")

            else:
                with open(photo_path, "rb") as photo:
                    sent = bot.send_photo(chat_id, photo, caption=msg, reply_markup=keyboard, parse_mode="HTML")
                    img_cache[photo_path] = sent.photo[-1].file_id
        else:
            bot.send_message(chat_id,"<i>Для работы с ботом\n"
                            "Подпишитесь на 👉  <a href='https://t.me/turkey_2change'>чат 2Change</a></i>",
                            parse_mode="HTML")
    if call.data == "tr_card_request":
        msg = ("⚡️Менеджер свяжется с вами в ближайшее <b>рабочее</b> время\n"
               "🕰<b>Наш график работы:</b>\n"
               "Пн-Сб: 10:00 - 20:00\n"
               "Вс и последняя суббота месяца:\n"
               "<b>выходной</b>")
        bot.send_message(chat_id, msg, parse_mode="HTML")
    bot.answer_callback_query(call.id)
