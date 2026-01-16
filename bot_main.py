import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime

from utils import logger,  day_off
from database_main import QueueDB
from converter import FinInstr

#глобали
img_cache={}
id_cache={}
user_calc_states={}
currency_names = {"rub":"<b>RUB🇷🇺</b>",
                  "usd":"<b>USDT🪙</b>",
                  "try":"<b>TRY🇹🇷</b>",
                  "try_cash":"<b>💰TRY🇹🇷</b>",
                  "thb":"<b>THB🇹🇭</b>",
                  "thb_cash":"<b>💰THB🇹🇭</b>",
                  "cny":"<b>CNY🇨🇳</b>"}
admin_change_coef_states= {}

admin_id = (57713855, 22231230, 5777995768)
manager_chat_id = -1003210623925 #НЕ ЗАБУДЬ ПОМЕНЯТЬ ПРОВЕРКИ НА ПОДПИСКУ ДЛЯ РФ И ТАЙ
tr_chat_username = "@asas_magov"


class MyExceptionHandler(telebot.ExceptionHandler):

    def handle(self, exception):

        message = f"Ошибка в боте: {exception}"
        logger.error(message, exc_info=True)
        # Здесь можно добавить логирование ошибки, например через logger
        bot.send_message(admin_id[0], message)
        return True
class ApplicationCreator:
    def __init__(self, country:int=None,client_name=None, reason:str=None, currency1=None, currency2=None,amount1=None, amount2=None, time=None ):#AMOUNT2 БУДЕТ ВЫСЧИТЫВАТЬСЯ ИСХОДЯ ИЗ ФУНКЦИИ ИНВЕСТИНГА
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
        """country_names = {1: "🇹🇷Турция", 2: "🇷🇺Россия", 3: "🇹🇭Тайланд", 4: "🇨🇳Китай"}"""

        msg = ""
        country_names = {0:"Страна не указана", 1: "🇹🇷Турция", 2: "🇷🇺Россия", 3: "🇹🇭Тайланд", 4: "🇨🇳Китай"}
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
    if user_id == 300423184:
        logger.info("Тестировщик!")
        return True
    elif country == 1: #tr
        logger.info(f"Проверяем подписку id={user_id} на Турецкий чат...")

        chat_member = bot.get_chat_member(tr_chat_username, user_id)

        if chat_member.status in ("creator", "administrator", "member"):
            logger.info("Чел подписан!")
            return True
        else:
            logger.info("Чел не подписан!")
            return False

    logger.error("Не проверили, возвращаем None!!!")
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
def send_application(user_id,user_name,chat_id,reason=None,country=None,amount1=None,amount2=None,currency1=None,currency2=None):
    msg = ("⚡️Позвали менеджера, скоро с вами свяжутся, ожидайте\n"
           "🕰<b>Наш график работы:</b>\n"
           "Пн-Сб: 10:00 - 20:00\n"
           "Вс и последняя суббота месяца:\n"
           "<b>выходной</b>"
           )
    if day_off():
        qdb.add_to_queue(country=country, tg_id=user_id,name=user_name, reason=reason,amount1=amount1,amount2=amount2,currency1=currency1,currency2=currency2)
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
        apmake=ApplicationCreator(country=country, client_name=user_name, reason=reason,amount1=amount1,amount2=amount2, currency1=currency1,currency2=currency2)

        msg_admin = apmake.create()
        sent_msg= bot.send_message(manager_chat_id, msg_admin, parse_mode="HTML", reply_markup=keybord)
        id_cache[sent_msg.message_id] = (user_name, user_id)

        bot.send_message(chat_id, msg, parse_mode="HTML")
def send_indev(chat_id):
    msg =("<b>⚠️Мы пока дорабатываем эту функцию⚠️</b>\n\n"
          ""
          "💛Приносим свои извинения за неудобства, стараемся сделать ваш опыт использования бота комфортнее и лучше💛\n\n"
          ""
          "🔔Но наш менеджер всегда на связи, чтобы его позвать нажмите /manager")
    send_media("img/401.mp4", chat_id, caption=msg)





@bot.message_handler(commands=['start'])
def handle_start(message, not_first:bool=None):
    if message.chat.id in user_calc_states:
        del user_calc_states[message.chat.id]

    keyboard = InlineKeyboardMarkup(row_width=2)
    button1= InlineKeyboardButton( "🇹🇷 Турция", callback_data="tr_menu")
    button2 = InlineKeyboardButton("🇹🇭 Тайланд", callback_data="thai_menu")
    keyboard.row(button1, button2)
    keyboard.add(InlineKeyboardButton("🇨🇳Китай", callback_data="cn_menu"))

    keyboard.add(InlineKeyboardButton("🇷🇺 Россия/🪙Крипто-доллар USDT", callback_data="rf_menu"))
    keyboard.add(InlineKeyboardButton("📥Пополнить Bybit Card (🪙USDT)", callback_data="rf_menu"))
    keyboard.add(InlineKeyboardButton("🛡 Гарантии и отзывы", callback_data="comment_menu"))
    keyboard.row(InlineKeyboardButton("📲Симкарта eSIM", callback_data="esim_main"), InlineKeyboardButton("💳 Зарубежная карта", callback_data="tr_card_menu"))
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



    lines= qdb.get_from_queue()
    if lines:

        _, tg_id, country, client_name, amount1, amount2, currency1, currency2, reason, created_at = lines

        apmake = ApplicationCreator(country=country, client_name=client_name, amount1=amount1,amount2=amount2, currency1=currency1, currency2=currency2, reason=reason, time=created_at)
        msg = apmake.create()
        msg += "\n" + f"\n✅<b>Взят в работу:</b>\n<i>{datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}</i>\n\n💼Менеджер: {user_name} " + "\n" + f"\n➡️Cсылка на чат с клиентом:<a href='tg://user?id={tg_id}'>➡️ {client_name}</a>"
        msg += "\n" + f"\n⚡️Заявок в очереди: {qdb.count_rows()}"
        bot.send_message(message.chat.id, msg, parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, "Заявок в очереди не осталось.")
@bot.message_handler(commands=['change_coef'], func=lambda message: message.from_user.id in admin_id)
def change_coef(message):
    global admin_change_coef_states
    chat_id = message.chat.id

    row = qdb.get_currencies()
    rates = qdb.update_currency()
    if chat_id in admin_change_coef_states:
        del admin_change_coef_states[message.chat.id]


    (_, usd_rub,
     rub_usd,
     usd_try,
     cash_usd_try,
     rub_try,
     cash_rub_try,
     try_rub,
     usd_thb,
     cash_usd_thb,
     rub_thb,
     cash_rub_thb,
     rub_cny,
     usd_cny,
     cny_rub,
     updated_at)=row
    row1 = qdb.get_coef()

    (_,c_usd_rub,
     c_rub_usd,
     c_usd_try,
     c_cash_usd_try,
     c_rub_try,
     c_cash_rub_try,
     c_try_rub,
     c_usd_thb,
     c_cash_usd_thb,
     c_rub_thb,
     c_cash_rub_thb,
     c_rub_cny,
     c_usd_cny,
     c_cny_rub,
     updated_at)=row1[0]

    msg =(f"(🏛) USDT/RUB : {rates["usd_rub"]:.2f} RUB\n"
          f"Покупаем 1 USDT за {usd_rub:.2f} RUB ({c_usd_rub*100}%)\n"
          f"Продаем 1 USDT за {rub_usd:.2f} RUB ({c_rub_usd*100}%)\n\n"
          
        f"(🏛) USDT/TRY : {rates["usd_try"]:.2f} TRY\n" # ЛИРЫ ЗА 1 ДОЛЛАР
          f"Продаем {usd_try:.2f} TRY💳 за 1 USDT ({c_usd_try*100}%)\n" #ПЕРЕВОДОМ ЛИРЫ ЗА 1 ДОЛЛАР
          f"Продаем {cash_usd_try:.2f}💵 TRY за 1 USDT ({c_cash_usd_try*100}%)\n\n" #НАЛИЧНЫЕ ЛИРЫ ЗА 1 ДОЛЛАР
          
          f"(🏛) TRY/RUB : {rates["try_rub"]:.2f} RUB\n" #РУБЛЕЙ ЗА 1 ЛИРУ 
          f"Продаем 1 TRY💳  за {rub_try:.2f} RUB ({c_rub_try*100}%)\n"
          f"Продаем 1 TRY💵 за {cash_rub_try:.2f} RUB ({c_cash_rub_try*100}%)\n"
          f"Покупаем 1 TRY💳 за {try_rub:.2f} RUB ({c_try_rub*100}%)\n\n"
          f""
          
          
           f"(🏛) USDT/THB : {rates["usd_thb"]:.2f} THB\n"
          f"Продаем {usd_thb:.2f} THB💳 за 1 USDT ({c_usd_thb*100}%)\n"
          f"Продаем {cash_usd_thb:.2f} THB💵 за 1 USDT ({c_cash_usd_thb*100}%)\n\n"
           
           f"(🏛) THB/RUB : {rates["thb_rub"]:.2f} RUB\n"
          f"Продаем 1 THB💳 за {rub_thb:.2f} RUB ({c_rub_thb*100}%)\n"
          f"Продаем 1 THB 💵 за {cash_rub_thb:.2f} RUB ({c_cash_rub_thb*100}%)\n\n"
          f""
          f"(🏛) USDT/CNY : {rates["usd_cny"]:.2f} CNY\n"
          f"Продаем 1 USDT за {usd_cny:.2f} CNY ({c_usd_cny*100}%)\n\n"
          f"(🏛) CNY/RUB : {rates["cny_rub"]:.2f} CNY\n"
          f"Продаем 1 CNY за {rub_cny} RUB ({c_rub_cny*100}%)\n"
          f"Покупаем 1 CNY за {cny_rub} RUB ({c_cny_rub*100}%)\n")
    bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML")

    msg1 = "Выберите курс для изменения наценки:"
    keybord = InlineKeyboardMarkup(row_width=2)
    keybord.row(InlineKeyboardButton("🪙USDT→🇷🇺", callback_data="chc/usd_rub_c"),
                InlineKeyboardButton("🇷🇺→🪙USDT", callback_data="chc/rub_usd_c"))

    keybord.row(InlineKeyboardButton("🇷🇺→🇹🇷 (IBAN)", callback_data="chc/rub_try_c"),
                InlineKeyboardButton("🇷🇺→🇹🇷 (Наличные)", callback_data="chc/cash_rub_try_c"))

    keybord.row(InlineKeyboardButton("🪙USDT→🇹🇷 (IBAN)", callback_data="chc/usd_try_c"),
                InlineKeyboardButton("🪙USDT→🇹🇷 (Наличные)", callback_data="chc/cash_usd_try_c"))

    keybord.add(InlineKeyboardButton("🇹🇷→🇷🇺 (Переводом)", callback_data="chc/try_rub_c"))

    keybord.row(InlineKeyboardButton("🪙USDT→🇹🇭 (Переводом)", callback_data="chc/usd_thb_c"),
                InlineKeyboardButton("🪙USDT→🇹🇭 (Наличные)", callback_data="chc/cash_usd_thb_c"))

    keybord.row(InlineKeyboardButton("🇷🇺→🇹🇭 (Переводом)", callback_data="chc/rub_thb_c"),
                InlineKeyboardButton("🇷🇺→🇹🇭 (Наличные)", callback_data="chc/cash_rub_thb_c"))
    keybord.add(InlineKeyboardButton("🇷🇺→🇨🇳CNY (юань)", callback_data="chc/rub_cny_c"), )
    keybord.row(InlineKeyboardButton("🪙USDT→🇨🇳CNY (юань)", callback_data="chc/usd_cny_c"), InlineKeyboardButton("🇳CNY (юань)→🇷🇺", callback_data="chc/cny_rub_c"))


    bot.send_message(chat_id, msg1, reply_markup=keybord, parse_mode="HTML")






@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global user_calc_states, admin_change_coef_states
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    last_name = call.from_user.last_name or ""
    user_name = (call.from_user.first_name or "") + (" " + last_name if last_name else "")
    message_id = call.message.message_id

    #ГЛАВНОЕ МЕНЮ БЛОК
    if call.data=="main_menu":
        handle_start(call.message, True)
    if call.data=="tr_menu":
        if check_subscribtion(user_id, 1):
            keyboard = InlineKeyboardMarkup(row_width=2)
            keyboard.add(InlineKeyboardButton("✏️Калькулятор | Оставить заявку", callback_data="calc_tr"))
            keyboard.add(InlineKeyboardButton("📈Актуальный курс", callback_data="currency_menu"))
            keyboard.add(InlineKeyboardButton("🎁Получить бесплатно eSim", callback_data="esim_tr"))
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
    if call.data =="rf_menu":
        if check_subscribtion(user_id, 1):
            finstr = FinInstr()
            msg = finstr.show_currency(country=2)
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("✏️Рассчитать сумму", callback_data="calc_rf"))
            keyboard.add(InlineKeyboardButton("❔Задать вопрос", callback_data="request/❔вопрос про курсы валют/1"))
            bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)
        else:
            bot.send_message(chat_id,"<i>Для работы с ботом\n"
                            "Подпишитесь на 👉  <a href='https://t.me/turkey_2change'>чат 2Change</a></i>",
                            parse_mode="HTML")
    if call.data == "thai_menu":
        if check_subscribtion(user_id, 1):
            finstr = FinInstr()
            msg = finstr.show_currency(country=3)
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("✏️Рассчитать сумму", callback_data="calc_thai"))
            keyboard.add(InlineKeyboardButton("💳Зарубежная карта", callback_data="tr_card_menu"))
            keyboard.add(InlineKeyboardButton("❔Задать вопрос", callback_data="request/❔вопрос про курсы валют/1"))
            bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)
        else:
            bot.send_message(chat_id,"<i>Для работы с ботом\n"
                            "Подпишитесь на 👉  <a href='https://t.me/turkey_2change'>чат 2Change</a></i>",
                            parse_mode="HTML")
    if call.data == "cn_menu":
        if check_subscribtion(user_id, 1):
            finstr = FinInstr()
            msg = finstr.show_currency(country=3)
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("✏️Рассчитать сумму", callback_data="calc_cn"))
            keyboard.add(InlineKeyboardButton("💳Зарубежная карта", callback_data="tr_card_menu"))
            keyboard.add(InlineKeyboardButton("❔Задать вопрос", callback_data="request/❔вопрос про курсы валют/4"))
            bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)
        else:
            bot.send_message(chat_id,"<i>Для работы с ботом\n"
                            "Подпишитесь на 👉  <a href='https://t.me/turkey_2change'>чат 2Change</a></i>",
                            parse_mode="HTML")

    if call.data == "comment_menu":
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
    if call.data.startswith("esim"):
        if call.data == "esim_tr":
            if check_subscribtion(user_id, 1):
                keyboard = InlineKeyboardMarkup()
                keyboard.add(
                    InlineKeyboardButton("Оставить заявку✅", callback_data="request/🎁 бесплатная eSIM на 1ГБ/1"))
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
                send_media("img/esim.jpg", chat_id, msg, reply_markup=keyboard)
            else:
                bot.send_message(chat_id, "<i>Для работы с ботом\n"
                                          "Подпишитесь на 👉  <a href='https://t.me/turkey_2change'>чат 2Change</a></i>",
                                 parse_mode="HTML")
        if call.data == "esim_main":
            send_indev(chat_id)

    if call.data=="currency_menu":
        finstr = FinInstr()
        msg = finstr.show_currency(country=1)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✏️Рассчитать сумму", callback_data="calc"))
        keyboard.add(InlineKeyboardButton("❔Задать вопрос", callback_data="request/❔вопрос про курсы валют/1"))
        bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)



    #МЕНЮ ТУРЦИИ
    if call.data=="tr_card_menu":
        if check_subscribtion(user_id, 1):
            photo_path = "img/card.jpg"
            msg =("💳 Оформим зарубежную карту Visa за 5 минут!\n\n"
                 "🌍 Оплата и снятие наличных  по всему миру\n"
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

    #ТЕХНИЧЕСКИЕ ЛОВЦЫ
    if call.data.startswith("request/"):
        _, request, country= call.data.split("/")
        send_application(user_id, user_name, chat_id,country=int(country),reason=request)
    if call.data.startswith("exchange/"):

        _, currency1, currency2, country = call.data.split("/")
        if chat_id in user_calc_states:
            del user_calc_states[chat_id]
        user_calc_states= {
            chat_id: {

            'currency1': currency1,
            'currency2': currency2,
            'country': country,
            "amount1": None,
            "amount2": None}
        }
        logger.info(f"Добавлено состояние чата {chat_id}")
        min_sum = {"rub/try_cash":"\n• Через банкомат: от <b>10750₽</b>\n"
                                  "• В офисе: от <b>100 000 рублей</b>",
                   "rub/try":"<b>5000₽ (~2500 ₺)</b>",
                   "usd/try_cash":"<b>132 USDT</b>",
                   "usd/try":"<b>70 USDT (~2500₺)</b>",
                   "try/rub":"<b>2000 ₺</b>",
                   "rub/thb_cash":"<b>19390 ₽ (~ 7 000 бат)</b>",
                   "rub/thb":"<b>19390 ₽ (~ 7 000 бат)</b>",
                   "usd/thb_cash":"<b>250 USDT</b>",
                   "usd/thb":"<b>250 USDT</b>",
                   "rub/usd":"<b>30 000₽</b>",
                   "usd/rub":"<b>500 USDT</b>",
                   "rub/cny":"<b>6285₽</b>",
                   "usd/cny":"<b>76 USDT</b>",
                   "cny/rub":"<b>300 CNY</b>"}

        countries_menu = {"1":"tr_menu", "2":"rf_menu", "3":"thai_menu", "4":"cn_menu"}
        keybord = InlineKeyboardMarkup()
        keybord.add(InlineKeyboardButton("◀️Назад", callback_data=countries_menu[country]))
        msg = (f"✏️ Введите сумму в {currency_names[currency1]}\n"
               f"<i>Только цифры - без пробелов, точек и символов</i>\n\n"
               f""
               f"📌 Минимальная сумма: {min_sum[f'{currency1}/{currency2}']}")
        bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keybord)
        bot.register_next_step_handler(call.message, process_amount)
    if call.data.startswith("calc"):
        if call.data == "calc_rf":
            msg = "💸<i>Выберите валюту для обмена:</i>"
            keybord1 = InlineKeyboardMarkup(row_width=2)
            keybord1.row(InlineKeyboardButton("🪙USDT→🇷🇺", callback_data="exchange/usd/rub/2"),
                        InlineKeyboardButton("🇷🇺→🪙USDT", callback_data="exchange/rub/usd/2"))
            keybord1.row(InlineKeyboardButton("💰Иные валюты (менеджер)", callback_data="request/💰Обмен иных валют/1"),
                        InlineKeyboardButton("◀️Назад", callback_data="rf_menu"))
            bot.send_message(chat_id, msg, reply_markup=keybord1, parse_mode="HTML")
        elif call.data == "calc_thai":
            msg = "💸<i>Выберите валюту для обмена:</i>"
            keybord2 = InlineKeyboardMarkup(row_width=2)
            keybord2.row(InlineKeyboardButton("🪙USDT→🇹🇭 (Переводом)", callback_data="exchange/usd/thb/3"),
                        InlineKeyboardButton("🪙USDT→🇹🇭 (Наличные)", callback_data="exchange/usd/thb_cash/3"))

            keybord2.row(InlineKeyboardButton("🇷🇺→🇹🇭 (Переводом)", callback_data="exchange/rub/thb/3"),
                        InlineKeyboardButton("🇷🇺→🇹🇭 (Наличные)", callback_data="exchange/rub/thb_cash/3"))
            keybord2.row(InlineKeyboardButton("💰Иные валюты (менеджер)", callback_data="request/💰Обмен иных валют/1"),
                         InlineKeyboardButton("◀️Назад", callback_data="thai_menu"))
            bot.send_message(chat_id, msg, reply_markup=keybord2, parse_mode="HTML")
        elif call.data == "calc_tr":
            msg = "💸<i>Выберите валюту для обмена:</i>"
            keybord3 = InlineKeyboardMarkup(row_width=2)
            keybord3.row(InlineKeyboardButton("🇷🇺→🇹🇷 (IBAN)", callback_data="exchange/rub/try/1"),
                        InlineKeyboardButton("🇷🇺→🇹🇷 (Наличные)", callback_data="exchange/rub/try_cash/1"))

            keybord3.row(InlineKeyboardButton("🪙USDT→🇹🇷 (IBAN)", callback_data="exchange/usd/try/1"),
                              InlineKeyboardButton("🪙USDT→🇹🇷 (Наличные)", callback_data="exchange/usd/try_cash/1"))

            keybord3.add(InlineKeyboardButton("🇹🇷→🇷🇺 (Переводом)", callback_data="exchange/try/rub/1"))
            keybord3.row(InlineKeyboardButton("💰Иные валюты (менеджер)", callback_data="request/💰Обмен иных валют/1"),
                         InlineKeyboardButton("◀️Назад", callback_data="tr_menu"))
            bot.send_message(chat_id, msg, reply_markup=keybord3, parse_mode="HTML")
        elif call.data == "calc_cn":
            msg = "💸<i>Выберите валюту для обмена:</i>"
            keybord4 = InlineKeyboardMarkup()
            keybord4.add(InlineKeyboardButton("🇷🇺→🇨🇳CNY (юань)", callback_data="exchange/rub/cny/4"),)
            keybord4.add(InlineKeyboardButton("🪙USDT→🇨🇳CNY (юань)", callback_data="exchange/usd/cny/4"))
            keybord4.add(InlineKeyboardButton("🇳CNY (юань)→🇷🇺", callback_data="exchange/cny/rub/4"))
            keybord4.row(InlineKeyboardButton("💰Иные валюты (менеджер)", callback_data="request/💰Обмен иных валют/4"),
                         InlineKeyboardButton("◀️Назад", callback_data="cn_menu"))
            bot.send_message(chat_id, msg, reply_markup=keybord4, parse_mode="HTML")

    if call.data.startswith("chc"):
        _, table_name= call.data.split("/")
        admin_change_coef_states[chat_id] = table_name
        bot.send_message(chat_id,text="✏️Введите новую наценку в процентах в формате десятичной дроби (1.0 = 1%; 1.5=1.5%):\n\n"
                         "<i>Число не должно быть меньше 0</i>\n", parse_mode="HTML")
        bot.register_next_step_handler(call.message, process_coef_change)
    if call.data == "convert":
        app_state= user_calc_states.get(chat_id, {})
        currency1, currency2,country, amount1, amount2 = app_state["currency1"],app_state["currency2"],app_state["country"],app_state["amount1"],app_state["amount2"]


        send_application(user_id, user_name, chat_id,amount1=amount1,amount2=amount2, country=country, currency1=currency_names[currency1], currency2=currency_names[currency2])
        del user_calc_states[chat_id]
        logger.info(f"Удалено состояние чата {chat_id}!!!")
    if call.data == "contact_client": #ВОТ ЭТУ ХУЙНЮ НАДО ЗАСУНУТЬ В БАЗУ ДАННЫХ А ТО ПИЗДЕЦ

        client_name, client_id = id_cache[message_id]
        del id_cache[message_id]
        new_text = call.message.text + "\n" + f"\n✅<b>Взят в работу:</b>\n<i>{datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}</i>\n\n💼Менеджер: {user_name} " + "\n" + f"\n➡️Cсылка на чат с клиентом:<a href='tg://user?id={client_id}'>➡️ {client_name}</a>"
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text, parse_mode="HTML", reply_markup=None)
        logger.info(f"[ЗАЯВКА ВЗЯТА] Менеджер {user_name} взял заявку клиента {client_name} (id={client_id}) в {datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")} ")


















    bot.answer_callback_query(call.id)
def process_amount(message):
    global user_calc_states
    min_amount = {"rub/try_cash": 10750,
                  "rub/try": 5000,
                  "usd/try_cash": 132,
                  "usd/try": 70,
                  "try/rub": 2000,
                  "rub/thb_cash": 19390,
                  "rub/thb": 19390,
                  "usd/thb_cash": 250,
                  "usd/thb": 250,
                  "rub/usd": 30000,
                  "usd/rub": 500,
                  "rub/cny":6285,
                  "usd/cny": 76,
                  "cny/rub": 300,}
    fistr = FinInstr()
    chat_id = message.chat.id
    if chat_id not in user_calc_states:

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📋Главное меню", callback_data="main_menu"))
        bot.send_message(chat_id, "🕘Сессия истекла, попробуйте еще раз.", reply_markup=keyboard)
        return
    state = user_calc_states.get(chat_id, {})



    currency1 = state["currency1"]
    currency2= state["currency2"]
    min_exchange=min_amount[f"{currency1}/{currency2}"]


    if not message.text.isdigit():
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📋Главное меню", callback_data="main_menu"))
        bot.send_message(chat_id, "❌Введите, пожалуйста, только целое число.", reply_markup=keyboard)
        bot.register_next_step_handler(message, process_amount)
        return
    if int(message.text) < min_exchange:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📋Главное меню", callback_data="main_menu"))
        bot.send_message(chat_id, f"❌Число не должно быть меньше <b>{min_exchange} {currency_names[currency1]}</b>",parse_mode="HTML", reply_markup=keyboard)
        bot.register_next_step_handler(message, process_amount)
        return
    converted= fistr.convert_currencies(int(message.text), currency1, currency2)
    msg = (f"<b>Обмен:</b> {currency_names[currency1]} → {currency_names[currency2]}\n\n"
           f"<b>Вы отдаете:</b> {int(message.text)} {currency_names[currency1]}\n\n"
           f"<b>Вы получаете:</b> {converted} {currency_names[currency2]}\n\n"
           f""
           f"<b>Отправить заявку на обмен?</b>")
    user_calc_states[chat_id]["amount1"]=int(message.text)
    user_calc_states[chat_id]["amount2"]=converted
    print(user_calc_states)
    keybord = InlineKeyboardMarkup(row_width=2)
    keybord.row(InlineKeyboardButton("✅Обменять", callback_data=f"convert"),
                InlineKeyboardButton("❌Отмена", callback_data="main_menu"))
    bot.send_message(chat_id, msg, reply_markup=keybord, parse_mode="HTML")
def process_coef_change(message):
    chat_id = message.chat.id
    try:
        if not float(message.text):
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("📋Главное меню", callback_data="main_menu"))
            bot.send_message(chat_id, "❌Введите, пожалуйста, только десятичную дробь (например, 1.0)", reply_markup=keyboard)
            bot.register_next_step_handler(message, process_coef_change)
            return
        flmes = float(message.text)
        if flmes <= 0:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("📋Главное меню", callback_data="main_menu"))
            bot.send_message(chat_id, f"❌Число не должно быть меньше <b>0</b>",parse_mode="HTML", reply_markup=keyboard)
            bot.register_next_step_handler(message, process_amount)
            return
        flmes /= 100

        qdb.set_coef(admin_change_coef_states[chat_id], flmes)
        bot.send_message(chat_id, "✅Наценка изменена!")

    except Exception as e:
        bot.send_message(chat_id, f"Что-то пошло не так, уведомили программиста:\n\n"
                                  f"{e}")

