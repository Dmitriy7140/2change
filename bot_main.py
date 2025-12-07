import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime

from utils import logger,  day_off
from database_main import QueueDB
from converter import FinInstr

#глобали
img_cache={}
id_cache={}

admin_id = (57713855, 22231230)
manager_chat_id = -1003210623925
tr_chat_username = "@asas_magov"


class MyExceptionHandler(telebot.ExceptionHandler):

    def handle(self, exception):

        message = f"Ошибка в боте: {exception}"
        logger.error(message, exc_info=True)
        # Здесь можно добавить логирование ошибки, например через logger
        bot.send_message(admin_id[0], message)
        return True
class ApplicationCreator:
    def __init__(self, country:int=None,client_name=None, reason:str=None, currency1=None, currency2=None,amount1=None, amount2="n", time=None ):#AMOUNT2 БУДЕТ ВЫСЧИТЫВАТЬСЯ ИСХОДЯ ИЗ ФУНКЦИИ ИНВЕСТИНГА
        self.country = country
        self.client_name = client_name
        self.reason = reason
        self.currency1 = currency1
        self.currency2 = currency2
        self.amount1 = amount1
        self.amount2 = amount2
        if time is None:
            self.time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        else:
            self.time = time
    def create(self):
        """country_names = {1: "🇹🇷Турция", 2: "🇷🇺Россия", 3: "🇹🇭Тайланд", 4: "🇰🇷Корея"}"""
        msg = ""
        country_names = {0:"Страна не указана", 1: "🇹🇷Турция", 2: "🇷🇺Россия", 3: "🇹🇭Тайланд", 4: "🇰🇷Корея"}
        intro = country_names.get(self.country, "Страна не указана") +"\n"+f"👤Клиент: {self.client_name}"
        if self.amount1:
            main_body=""
            if self.currency1 and self.currency2:
                main_body =f"<b>🫵Отдаст: {self.amount1}</b> {self.currency1}" +'\n\n'+f"👉<b>Получит: {self.amount2}</b> {self.currency2}"
            elif self.currency1 and not self.currency2:
                main_body =f"<b>🫵Отдаст:{self.amount1}</b> {self.currency1}"+"\n\n"+f"<b>👉Получит:</b> 🤔Иную валюту."
            elif not self.currency1 and self.currency2:
                main_body=f"<b>🫵Отдаст: {self.amount1}</b> 🤔Иной валюты" +"\n\n"+f"<b>👉Получит:</b> {self.currency2}"
            elif not self.currency1 and not self.currency2:
                main_body=f"<b>🫵Отдаст: {self.amount1}</b> 🤔Иной валюты" +"\n\n"+f"<b>👉Получит:</b> 🤔Иную валюту."
            msg+= intro+"\n\n"+main_body+"\n\n"+f"🕘<i>{self.time}</i>"
            return msg
        else:

            msg += intro +"\n\n"+ f"\nПричина: {self.reason if self.reason else "осталась в тайне"}"+"\n\n"+f"🕘{self.time}"
            return msg


qdb=QueueDB()
bot = telebot.TeleBot( "8559812575:AAFducMZ0rp9WKCbo_pv8yyhkMAG8Drz6m8", exception_handler=MyExceptionHandler())


def check_subscribtion(user_id, country):
    if country == 1: #tr

        chat_member = bot.get_chat_member(tr_chat_username, user_id)

        if chat_member.status in ("creator", "administrator", "member"):

            return True
        else:

            return False
    return None


def send_media(path, chat_id, caption=None, reply_markup=None, parse_mode="HTML"):
    if path in img_cache:
        file_id = img_cache[path]
        if path.lower().endswith('.gif'):
            bot.send_animation(chat_id, file_id, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
        elif path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            bot.send_photo(chat_id, file_id, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
        else:  # mp4, avi и т.д.
            bot.send_video(chat_id, file_id, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
    else:
        with open(path, "rb") as media:
            if path.lower().endswith('.gif'):
                sent = bot.send_animation(chat_id, media, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
                img_cache[path] = sent.animation.file_id
            elif path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                sent = bot.send_photo(chat_id, media, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
                img_cache[path] = sent.photo[-1].file_id
            else:  # видео
                sent = bot.send_video(chat_id, media, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
                img_cache[path] = sent.video.file_id
def send_application(user_id,user_name,chat_id,reason=None,country=None,amount1=None,currency1=None,currency2=None):
    msg = ("⚡️Позвали менеджера, скоро с вами свяжутся, ожидайте\n"
           "🕰<b>Наш график работы:</b>\n"
           "Пн-Сб: 10:00 - 20:00\n"
           "Вс и последняя суббота месяца:\n"
           "<b>выходной</b>"
           )
    if day_off():
        qdb.add_to_queue(country=country, tg_id=user_id,name=user_name, reason=reason,amount=amount1,currency1=currency1,currency2=currency2)
        msg = ("🏄‍♂️<b>К СОЖАЛЕНИЮ, МЫ СЕЙЧАС НЕ РАБОТАЕМ</b>🏄‍♀️\n\n"
               "✅Добавили вашу заявку в очередь\n\n"
               "⚡️В <b>рабочее</b> время менеджер получит вашу заявку и свяжется с вами\n"
               "🕰<b>Наш график работы:</b>\n"
               "Пн-Сб: 10:00 - 20:00\n"
               "Вс и последняя суббота месяца:\n"
               "<b>выходной</b>"
               )
        bot.send_message(chat_id, msg, parse_mode="HTML")
        bot.send_message(manager_chat_id, f"🛑Новая заявка в очереди. Всего заявок: {qdb.count_rows()}\n\n"
                                          f"Нажмите /queue для отработки.", disable_notification=True)
    else:
        keybord = InlineKeyboardMarkup()
        keybord.add( InlineKeyboardButton("💬Связаться с клиентом", callback_data="contact_client"))
        apmake=ApplicationCreator(country=country, client_name=user_name, reason=reason,amount1=amount1,currency1=currency1,currency2=currency2)

        msg_admin = apmake.create()
        sent_msg= bot.send_message(manager_chat_id, msg_admin, parse_mode="HTML", reply_markup=keybord)
        id_cache[sent_msg.message_id] = (user_name, user_id)

        bot.send_message(chat_id, msg, parse_mode="HTML")


@bot.message_handler(commands=['start'])
def handle_start(message, not_first:bool=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1= InlineKeyboardButton( "🇹🇷 Турция", callback_data="tr_menu")
    button2 = InlineKeyboardButton("🇹🇭 Тайланд", callback_data="thai_menu")
    keyboard.row(button1, button2)

    keyboard.add(InlineKeyboardButton("🇷🇺 Россия", callback_data="rf_menu"))
    keyboard.add(InlineKeyboardButton("🛡 Гарантии и отзывы", callback_data="comment_menu"))
    keyboard.add(InlineKeyboardButton("💳 Зарубежная карта", callback_data="tr_card_menu"))
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

    send_media(path=video_path,chat_id=message.chat.id,reply_markup=keyboard,caption=msg)

@bot.message_handler(commands=['manager'])
def handle_manager(message):
    user_name = message.from_user.first_name + " " + message.from_user.last_name
    user_id = message.from_user.id
    if check_subscribtion(user_id,1):
        if day_off():
            qdb.add_to_queue(tg_id=user_id, name=user_name, reason="🔔вызов менеджера")
            msg = ("🏄‍♂️<b>К СОЖАЛЕНИЮ, МЫ СЕЙЧАС НЕ РАБОТАЕМ</b>🏄‍♀️\n\n"
                   "✅Добавили вашу заявку в очередь\n\n"
                   "⚡️В <b>рабочее</b> время менеджер получит вашу заявку и свяжется с вами\n"
                   "🕰<b>Наш график работы:</b>\n"
                   "Пн-Сб: 10:00 - 20:00\n"
                   "Вс и последняя суббота месяца:\n"
                   "<b>выходной</b>"
                   )
            bot.send_message(message.chat.id, msg, parse_mode="HTML")
        else:
            apmake = ApplicationCreator(client_name=user_name, reason="🔔вызов менеджера")
            msg = apmake.create()
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("💬Связаться с клиентом", callback_data="contact_client"))
            sent_msg = bot.send_message(manager_chat_id, msg, parse_mode="HTML", reply_markup=keyboard)
            id_cache[sent_msg.message_id] = (user_name, user_id)
            bot.send_message(message.chat.id, "⚡️Позвали менеджера, скоро с вами свяжутся, ожидайте\n"
                       "🕰<b>Наш график работы:</b>\n"
                       "Пн-Сб: 10:00 - 20:00\n"
                       "Вс и последняя суббота месяца:\n"
                       "<b>выходной</b>", parse_mode="HTML")
    else:
        bot.send_message(message.chat.id,"<i>Для работы с ботом\n"
                            "Подпишитесь на 👉  <a href='https://t.me/turkey_2change'>чат 2Change</a></i>", parse_mode="HTML")

@bot.message_handler(commands=['queue'], func=lambda message: message.from_user.id in admin_id)
def handle_queue(message):
    last_name = message.from_user.last_name or ""
    user_name = (message.from_user.first_name or "") + (" " + last_name if last_name else "")

    amount2= None

    lines= qdb.get_from_queue()
    if lines:

        _, tg_id, country, client_name, amount, currency1, currency2, reason, created_at = lines
        if amount and currency1 and currency2:

            amount2= "formula"
        apmake = ApplicationCreator(country=country, client_name=client_name, amount1=amount, amount2=amount2,currency1=currency1, currency2=currency2, reason=reason, time=created_at)
        msg = apmake.create()
        msg += "\n" + f"\n✅<b>Взят в работу:</b>\n<i>{datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}</i>\n\n💼Менеджер: {user_name} " + "\n" + f"\n➡️Cсылка на чат с клиентом:<a href='tg://user?id={tg_id}'>➡️ {client_name}</a>"
        msg += "\n" + f"\n⚡️Заявок в очереди: {qdb.count_rows()}"
        bot.send_message(message.chat.id, msg, parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, "Заявок в очереди не осталось.")





@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    last_name = call.from_user.last_name or ""
    user_name = (call.from_user.first_name or "") + (" " + last_name if last_name else "")
    message_id = call.message.message_id

    if call.data=="tr_menu":
        if check_subscribtion(user_id, 1):
            keyboard = InlineKeyboardMarkup(row_width=2)
            keyboard.add(InlineKeyboardButton("✏️Калькулятор | Оставить заявку", callback_data="calc"))
            keyboard.add(InlineKeyboardButton("📈Актуальный курс", callback_data="currency_menu"))
            keyboard.add(InlineKeyboardButton("🎁Получить бесплатно eSim", callback_data="tr_esim_menu"))
            keyboard.add(InlineKeyboardButton("💳Зарубежная карта", callback_data="tr_card_menu"))
            keyboard.add(InlineKeyboardButton("👤Менеджер", callback_data="request/🔔вызов менеджера/0"))
            button1= InlineKeyboardButton("💼Другие услуги", callback_data="other_menu")
            button2= InlineKeyboardButton("📋Главное меню", callback_data="main_menu")
            keyboard.row(button1, button2)
            send_media(path="img/turkey.jpg", chat_id=chat_id, caption='''🇹🇷<b>2Change — услуги в Турции\n\n🕒 График работы:</b>\nПн-Сб: 10:00 - 20:00 (Вс - выходной)\nОфис по записи''', parse_mode="HTML", reply_markup=keyboard)
        else:
            bot.send_message(chat_id,"<i>Для работы с ботом\n"
                            "Подпишитесь на 👉  <a href='https://t.me/turkey_2change'>чат 2Change</a></i>",
                            parse_mode="HTML")
    if call.data=="currency_menu":
        finstr = FinInstr()
        msg = finstr.show_currency()
        bot.send_message(chat_id, msg, parse_mode="HTML")
    if call.data=="tr_esim_menu":
        if check_subscribtion(user_id, 1):
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("Оставить заявку✅",callback_data="request/🎁 бесплатная eSIM на 1ГБ/1"))
            keyboard.add(InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
            msg = (
                "🎁 <b>Дарим электронную симкарту eSIM</b> — без условий и скрытых платежей!\n\n"
                "Хотите оставаться на связи в Турции без переплат? \n"
                "Ловите подарок — eSIM с интернетом <b>абсолютно бесплатно!</b>\n\n"
                "<b>📱 Что такое eSIM?</b>\n"
                "Это интернет за границей без физической sim-карты.\n"
                "Удобно, быстро, без визита в салон связи.\n\n"
                "💡 <b>Что вы получите?</b>\n"
                "✔️ Бесплатное подключение\n"
                "✔️ 1 ГБ интернета\n"
                "✔️ Выгодное пополнение при необходимости\n"
                "🇹🇷 <b>5 ГБ — 1900₽</b>\n"
                "🇹🇷 <b>10 ГБ — 2500₽</b>\n"
                "🇹🇷 <b>20 ГБ — 3300₽</b>\n\n"
                "🎁 <b>Бонус +10 ГБ трафика в подарок</b>, при обмене от 20 000 лир через QR!\n\n"
                "👇 <b>Оставьте заявку</b> или напишите менеджеру\n "
                "@ALEXANDRA_2CHANGE 👩🏻‍💼"
            )
            send_media("img/esim.jpg",chat_id,msg,reply_markup=keyboard)
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
    if call.data=="tr_card_menu":
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
            keyboard.add(InlineKeyboardButton("Оставить заявку✅", callback_data="request/💳зарубежная карта/1"))
            keyboard.add(InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
            send_media(photo_path, chat_id, msg, keyboard)
        else:
            bot.send_message(chat_id,"<i>Для работы с ботом\n"
                            "Подпишитесь на 👉  <a href='https://t.me/turkey_2change'>чат 2Change</a></i>",
                            parse_mode="HTML")
    if call.data.startswith("request/"):
        _, request, country= call.data.split("/")
        send_application(user_id, user_name, chat_id,country=int(country),reason=request)
    if call.data == "other_menu":
        msg=("👋 <b>Добро пожаловать!</b>\n"
             "Здесь вы можете ознакомиться со всеми видами услуг сервиса <b>2Change</b>.\n\n"
             "<i>Мы помогаем с 💸 переводами, расчётами, оплатами и 📦 сопроводительными услугами для работы с разными странами 🌍 и платформами.</i>\n\n"
             "<b>👇 Нажмите, чтобы узнать подробности</b>")
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("Наличные через банкомат (QR-код)", callback_data="tr_qr_menu"))
        button1, button2= InlineKeyboardButton("Перевод по IBAN", callback_data="tr_iban_menu"), InlineKeyboardButton("Наличные в офисе",callback_data="tr_office_cash_menu")
        keyboard.row(button1, button2)
        keyboard.add(InlineKeyboardButton("Симкарта eSim📲", callback_data="tr_esim_menu"))
        keyboard.add(InlineKeyboardButton("Денежные переводы💸", callback_data="tr_cash_transactions_menu"))
        keyboard.add(InlineKeyboardButton("Открытие счета в турецком банке🇹🇷", callback_data="tr_acc"))
        keyboard.add(InlineKeyboardButton("Онлайн-сервисы и букинги💻", callback_data="tr_services_booking_menu"))
        keyboard.add(InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
        bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)
    if call.data == "tr_qr_menu":
        msg = ("<b>💵 Как обменять РУБЛИ и USDT на наличные лиры за 5 минут?</b>\n\n"

        "Вы можете быстро и без карты получить наличные лиры в любом банкомате Турции!\n\n"

        "<b>👥 Кому подойдёт:</b>\n"
        "— Туристам и тем, у кого нет турецкой карты\n"
        "— Кто ценит сервис и поддержку на русском языке\n\n"

        "<b>🔄 Как это работает:</b>\n"
        "— Оставьте заявку в боте или напишите @ALEXANDRA_2CHANGE\n"
        "— Переведите рубли или USDT\n"
        "— Отправьте нам фото QR-кода на экране банкомата\n"
        "— Заберите наличные ₺\n\n"

        "<b>💰 Лимиты: от 5 000₺ до 100 000₺\n"
        "📶 Требование: телефон с интернетом</b>\n"
        "Бесплатно eSIM +1Гб можно оформить у менеджера — /manager\n"
        "<a href='https://telegra.ph/Nalichnye-cherez-QR-kod-v-bankomate-05-21'>📎 Подробнее и FAQ</a>\n\n"

        "<b>📊 Рассчитайте обмен или оставьте заявку 👇</b>"
        )
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✏️Рассчитать обмен", callback_data="calc"))
        keyboard.add(InlineKeyboardButton("👤Задать вопрос", callback_data="request/🏧Выдача через банкомат по QR/1"))
        keyboard.add(InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
        send_media("img/turkey_qr.MP4", chat_id, msg, keyboard)
    if call.data == "tr_iban_menu":
        msg = ("<b>💸 Обмен RUB или USDT → лиры на IBAN за 2 минуты!</b>\n\n"
               "<b>👤 Кому подойдёт:</b>\n"
               "— Владельцам карт турецких банков\n"
               "— Кто ценит скорость и удобство \n\n"
               ""
               "<b>🔄 Как это работает:</b>\n"
               "— Оставьте заявку в боте или напишите @ALEXANDRA_2CHANGE\n"
               "— Переведите рубли или USDT\n"
               "— Отправьте IBAN и ФИО (на английском)\n"
               "— Получите ₺ лиры на счёт\n\n"
               "💰 Лимиты: от 2 000₺ до 500 000₺\n"
               "<a href='https://telegra.ph/IBAN-05-21'>📎Подробнее и FAQ </a>\n\n"
               "👇 Рассчитайте обмен или задайте вопрос")
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✏️Рассчитать обмен", callback_data="calc"))
        keyboard.add(InlineKeyboardButton("👤Задать вопрос", callback_data="request/🔄IBAN-перевод/1"))
        keyboard.add(InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
        send_media("img/tr_iban.jpg", chat_id, msg, keyboard)
    if call.data=="tr_office_cash_menu":
        msg = ("<b>🏢 Получение наличных лир в офисе — Стамбул, Анталья, Аланья\n\n"
                ""
                "👥 Кому подойдёт:</b>\n"
                "— Кто хочет обменять крупную сумму\n"
                "— Кто предпочитает личную встречу\n\n"
                ""
                "<b>🔄 Как это работает:</b>\n"
                "— Приезжаете по записи\n"
                "— Переводите рубли\n"
                "— Получаете наличные лиры\n"
                "— Доллары или евро по запросу\n\n"
                "💰 Сумма: от 100 000₽\n"
                "<b>🕒 По записи минимум за 1 час</b>\n"
                "<a href='https://telegra.ph/Ofis-05-21-9'>📎 Подробнее и FAQ</a>\n\n"
                ""
                "<b>Рассчитайте обмен или оставьте заявку 👇</b>")
        keyboard= InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✏️Рассчитать обмен", callback_data="calc"))
        keyboard.add(InlineKeyboardButton("👤Задать вопрос", callback_data="request/💰Выдача наличных в офисе/1"))
        keyboard.add(InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
        bot.send_message(chat_id=chat_id, text=msg, reply_markup=keyboard, parse_mode="HTML")
    if call.data=="tr_cash_transactions_menu":
        msg = ("Возможно получение на карту/счет, а также получение наличных.\n\n"
               "Доступны для перевода:\n"
               "🇪🇺 Европа\n🇦🇷 Аргентина\n🇧🇾 Беларусь\n🇧🇷 Бразилия\n🇬🇪 Грузия\n🇮🇳 Индия\n🇮🇩 Индонезия\n🇰🇿 Казахстан\n🇨🇦 Канада\n🇨🇳 Китай\n🇰🇷 Корея\n🇲🇽 Мексика\n🇦🇪 ОАЭ\n🇷🇺 Россия\n🇺🇸 США\n🇹🇭 Таиланд\n🇹🇷 Турция\n🇺🇿 Узбекистан и другие страны"
               "\nWise\nSepa\nRevolut\nAlipay/Wechat\nPaypal\n\n"
               ""
               "👇Оставьте заявку, и менеджер @ALEXANDRA_2CHANGE ответит на ваши вопросы")

        keyboard = InlineKeyboardMarkup()

        keyboard.add(InlineKeyboardButton("✅Узнать у менеджера", callback_data="request/💸Денежные переводы/0"))
        keyboard.add(InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
        bot.send_message( chat_id, msg, reply_markup=keyboard)
    if call.data=="tr_acc":
        msg = ("<b>🏦 Оформление турецкой банковской карты — дистанционно</b>\n\n"
               ""
               "Без депозита. Без ВНЖ. Без визита в отделение.\n\n"
               ""
               "<b>📌 Доступные банки:\n• 🔵 DenizBank\n• 🟡 VakıfBank\n• 🟥 Ziraat Bankası</b>\n\n"
               ""
               "<b>Необходимые документы:</b>\n• 🛂 Загранпаспорт\n• 🧾 Турецкий ИНН (если нет — поможем оформить)\n\n"
               ""
               "👇Оставьте заявку, и менеджер @ALEXANDRA_2CHANGE ответит на ваши вопросы.")


        keyboard = InlineKeyboardMarkup()

        keyboard.add(InlineKeyboardButton("✅Узнать у менеджера", callback_data="request/Счет в банке 🇹🇷/1"))
        keyboard.add(InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
        bot.send_message(chat_id, msg, reply_markup=keyboard, parse_mode="HTML")
    if call.data=="tr_services_booking_menu":
        msg = ("<b>💳 Оплата любых онлайн-сервисов за 3 минуты</b>\n\n"
               ""
               "Airbnb, Agoda, Booking, IKEA, PS Store, Netflix, визы, аренда авто и многое другое — оплачиваем быстро и без лишних шагов.\n\n💸"
               ""
               "<b>Условия:</b>\n"
               "• Оплата через наш аккаунт или ваш\n"
               "• Комиссия — фиксированная: 300 ₽\n"
               "• Оплата принимается в рублях (любой банк) и USDT\n\n"
               ""
               "<b>📌 Как это работает?</b>\n\n"
               "1. 🔗 Отправьте <a href='https://t.me/ALEXANDRA_2CHANGE'>👤 менеджеру</a> ссылку на сервис и нужные товары/услуги\n"
               "2. 📊 Получите расчёт в рублях\n"
               "3. 💵 Оплатите удобным способом\n"
               "4. ✅ Мы оплачиваем заказ или выдаём карту для самостоятельной оплаты (в зависимости от сервиса)\n\n"
               ""
               "<b>❓ Остались вопросы?</b>\n"
               "Оставьте заявку — всё расскажем и подскажем 👇")

        keyboard = InlineKeyboardMarkup()

        keyboard.add(
            InlineKeyboardButton("✅Узнать у менеджера", callback_data="request/Онлайн-сервисы  💻/1"))
        keyboard.add(InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
        bot.send_message(chat_id, msg, reply_markup=keyboard, parse_mode="HTML")









    if call.data == "contact_client":

        client_name, client_id = id_cache[message_id]
        del id_cache[message_id]
        new_text = call.message.text + "\n" + f"\n✅<b>Взят в работу:</b>\n<i>{datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}</i>\n\n💼Менеджер: {user_name} " + "\n" + f"\n➡️Cсылка на чат с клиентом:<a href='tg://user?id={client_id}'>➡️ {client_name}</a>"
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text, parse_mode="HTML", reply_markup=None)
    bot.answer_callback_query(call.id)