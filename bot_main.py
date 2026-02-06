import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime, time

from utils import logger,  day_off
from database_main import QueueDB
from converter import FinInstr

#глобали
img_cache={}

user_calc_states={}
currency_names = {"rub":"<b>RUB🇷🇺</b>",
                  "usd":"<b>USDT🪙</b>",
                  "try":"<b>TRY🇹🇷</b>",
                  "try_cash":"<b>Наличные TRY🇹🇷</b>",
                  "thb":"<b>THB🇹🇭</b>",
                  "thb_cash":"<b>Наличные THB🇹🇭</b>",
                  "cny":"<b>CNY🇨🇳</b>",
                  "krw":"<b>KRW🇰🇷</b>"}
admin_change_coef_states= {}
to_edit= {}

admin_id = (57713855, 22231230, 5777995768, 177592380, 398673425, 5853188702)
manager_chat_id = -1001520870092

tr_chat_username = "@turkey_2change"
kr_chat_username = "@korea_obmen1"

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
        """country_names = {1: "🇹🇷Турция", 2: "🇷🇺Россия", 3: "🇹🇭Тайланд", 4: "🇨🇳Китай", 5: "Корея", 6 : ОАЭ}"""

        msg = ""
        country_names = {0:"Страна не указана", 1: "🇹🇷Турция", 2: "🇷🇺Россия", 3: "🇹🇭Тайланд", 4: "🇨🇳Китай", 5:"🇰🇷Корея", 6:"🇦🇪ОАЭ"}
        intro = country_names.get(self.country, "Страна не указана") +"\n"+f"👤Клиент: {self.client_name}"
        if self.amount1:
            main_body =f"<b>🫵Отдаст: {self.amount1}</b> {self.currency1}" +'\n\n'+f"👉<b>Получит: {self.amount2}</b> {self.currency2}"
            rate =""
            if float(self.amount2) > float(self.amount1):
                rate = f"<b>📈Курс:</b> {float(self.amount2) / float(self.amount1):.2f}"
            elif float(self.amount1) > float(self.amount2):
                rate = f"<b>📈Курс:</b> {float(self.amount1) / float(self.amount2):.2f}"



            msg+= intro+"\n\n"+main_body+"\n\n"+rate+"\n\n"+f"🕘<i>{self.time}</i>"
            return msg
        else:

            msg += intro +"\n\n"+ f"\nПричина: {self.reason if self.reason else "осталась в тайне"}"+"\n\n"+f"🕘{self.time}"
            return msg


qdb=QueueDB()
bot = telebot.TeleBot( "8236711902:AAEvpg2ItZeRw25-EUyg0SI5DVYBbP23LLM", exception_handler=MyExceptionHandler())


def check_subscribtion(user_id, country):

    if country == 1: #tr
        logger.info(f"Проверяем подписку id={user_id} на Турецкий чат...")

        chat_member = bot.get_chat_member(tr_chat_username, user_id)

        if chat_member.status in ("creator", "administrator", "member"):
            logger.info("Чел подписан!")
            return True
        else:
            logger.info("Чел не подписан!")
            return False
    elif country == 5:
        chat_member = bot.get_chat_member(kr_chat_username, user_id)
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
def send_application(user_id,user_name,chat_id,user_ref, reason=None,country=None,amount1=None,amount2=None,currency1=None,currency2=None):
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

    else:
        keybord = InlineKeyboardMarkup()
        keybord.add( InlineKeyboardButton("💬Связаться с клиентом", callback_data="contact_client"))
        apmake=ApplicationCreator(country=country, client_name=user_name, reason=reason,amount1=amount1,amount2=amount2, currency1=currency1,currency2=currency2)

        msg_admin = apmake.create()
        sent_msg= bot.send_message(manager_chat_id, msg_admin, parse_mode="HTML", reply_markup=keybord)

        if qdb.set_user_name(sent_msg.message_id, user_id, user_ref):

            bot.send_message(chat_id, msg, parse_mode="HTML")
        else:
            bot.send_message(chat_id, "⛔️Менеджер не сможет вам написать из-за ваших настроек приватности⛔️\n "
                                      "Включите видимость вашего аккаунта по ссылке в настройках приватности, или напишите @ALEXANDRA_2CHANGE", parse_mode="HTML")
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
    keyboard.row(InlineKeyboardButton("🇨🇳Китай", callback_data="cn_menu"), InlineKeyboardButton("🇰🇷Корея", callback_data="kr_menu"))

    keyboard.add(InlineKeyboardButton("🇷🇺 Россия (USDT)", callback_data="rf_menu"))
    keyboard.add(InlineKeyboardButton("📥Пополнить Bybit Card (🪙USDT)", callback_data="bybit_add"))
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
    user_ref = message.from_user.username
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

            if qdb.set_user_name(sent_msg.message_id, user_id, user_ref):
                bot.send_message(message.chat.id, "⚡️Позвали менеджера, скоро с вами свяжутся, ожидайте\n"
                           "🕰<b>Наш график работы:</b>\n"
                           "Пн-Сб: 10:00 - 20:00\n"
                           "Вс и последняя суббота месяца:\n"
                           "<b>выходной</b>", parse_mode="HTML")
            else:
                bot.send_message(message.chat.id, "⛔️Менеджер не сможет вам написать из-за ваших настроек приватности⛔️\n "
                                          "Включите видимость вашего аккаунта по ссылке в настройках приватности, или напишите @ALEXANDRA_2CHANGE",
                                 parse_mode="HTML")
    else:
        bot.send_message(message.chat.id,"<i>Для работы с ботом\n"
                            "Подпишитесь на 👉  <a href='https://t.me/turkey_2change'>чат 2Change</a></i>", parse_mode="HTML")





def handle_queue():




    lines= qdb.get_from_queue(True)
    if lines:
        for i in lines:
            _, tg_id, country, client_name, amount1, amount2, currency1, currency2, reason, created_at = i

            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton("✅",callback_data=f"apq/y/{tg_id}"), InlineKeyboardButton("❌",callback_data=f"apq/n/{tg_id}"))
            bot.send_message(tg_id, f"Здравствуйте, {client_name}!\n\n"
                                    f"Подскажите, пожалуйста, актуальна ли Ваша заявка?\n\n"
                                    f"{reason if reason else f'<b>Обмен:</b> {currency1} → {currency2}\n\nСумма: {amount1} {currency1}'}",
                             reply_markup=keyboard, parse_mode="HTML")
            time.sleep(0.003)


    else:
        bot.send_message(manager_chat_id, "Заявок в очереди нет.")
        return
@bot.message_handler(commands=['change_coef'], func=lambda message: message.from_user.id in admin_id)# func=lambda message: message.from_user.id in admin_id)
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
     usd_krw,
     krw_usd,
     rub_krw,
     krw_rub,
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
     usd_krw_c,
     krw_usd_c,
     rub_krw_c,
     krw_rub_c,
     updated_at)=row1[0]

    msg =(f""
          f"(🏛) USDT/RUB : {rates["usd_rub"]:.2f} RUB\n"
          f"Покупаем 1 USDT за {usd_rub:.2f} RUB ({c_usd_rub*100}%)\n"
          f"Продаем 1 USDT за {rub_usd:.2f} RUB ({c_rub_usd*100}%)\n\n"
          f""
          
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
          f"Покупаем 1 USDT за {usd_cny:.2f} CNY ({c_usd_cny*100}%)\n\n"
          f"(🏛) CNY/RUB : {rates["rub_cny"]:.2f} CNY\n"
          f"Продаем 1 CNY за {rub_cny:.2f} RUB ({c_rub_cny*100}%)\n"
          f"Покупаем 1 CNY за {cny_rub:.2f} RUB ({c_cny_rub*100}%)\n\n"
          f""
          f"(🏛) KRW/RUB : {rates["krw_rub"]:.2f} KRW\n"
          f"Продаем 1 RUB за {krw_rub:.2f} KRW ({krw_rub_c*100}%)\n"
          f"Покупаем 1 RUB за {rub_krw:.2f} KRW ({rub_krw_c*100}%)\n\n"
          f"(🏛) KRW/USDT : {rates["krw_usd"]:.2f} KRW\n"
          f"Продаем 1 USDT за {krw_usd:.2f} KRW ({krw_usd_c*100}%)\n"
          f"Покупаем 1 USDT за {usd_krw:.2f} KRW ({usd_krw_c*100}%)")
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
    keybord.row(InlineKeyboardButton("🪙USDT→🇨🇳CNY (юань)", callback_data="chc/usd_cny_c"), InlineKeyboardButton("🇨🇳CNY (юань)→🇷🇺", callback_data="chc/cny_rub_c"))

    keybord.row(InlineKeyboardButton("🇰🇷 KRW → 🇷🇺RUB", callback_data="chc/krw_rub_c"), InlineKeyboardButton("🇰🇷 KRW  → 🪙 USDT", callback_data="chc/krw_usd_c"))
    keybord.row(InlineKeyboardButton("🇷🇺RUB → 🇰🇷 KRW ", callback_data="chc/rub_krw_c"),InlineKeyboardButton("🪙 USDT → 🇰🇷 KRW ", callback_data="chc/usd_krw_c"))



    bot.send_message(chat_id, msg1, reply_markup=keybord, parse_mode="HTML")






@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global user_calc_states, admin_change_coef_states, to_edit
    user_id = call.from_user.id
    user_ref = call.from_user.username
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
            keyboard.add(InlineKeyboardButton("📈Актуальный курс", callback_data="tr_currency_menu"))
            keyboard.add(InlineKeyboardButton("🎁Получить бесплатно eSim", callback_data="esim_tr"))
            # keyboard.add(InlineKeyboardButton("💳Зарубежная карта", callback_data="tr_card_menu"))
            # keyboard.add(InlineKeyboardButton("👤Менеджер", callback_data="request/🔔вызов менеджера/0"))
            # button1= InlineKeyboardButton("💼Другие услуги", callback_data="other_menu")
            button2= InlineKeyboardButton("📋Главное меню", callback_data="main_menu")
            keyboard.add( button2)
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
            keyboard.add(InlineKeyboardButton("❔Задать вопрос", callback_data="request/❔вопрос про курсы валют/2"))
            keyboard.add(InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
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
            keyboard.add(InlineKeyboardButton("❔Задать вопрос", callback_data="request/❔вопрос про курсы валют/3"))
            keyboard.add(InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
            bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)
        else:
            bot.send_message(chat_id,"<i>Для работы с ботом\n"
                            "Подпишитесь на 👉  <a href='https://t.me/turkey_2change'>чат 2Change</a></i>",
                            parse_mode="HTML")
    if call.data == "cn_menu":
        if check_subscribtion(user_id, 1):
            msg = ("<b>🇨🇳 Комплексная подготовка к поездке в Китай: Alipay, симкарта eSIM и обмен рублей</b>\n\n"
                   ""
                   "Хотите приехать в Китай и сразу <b>платить и быть на связи?</b>\n\n"
                   ""
                   "<b>С нами — просто! За 5 минут:</b>\n"
                   "▪️ <b>Alipay</b> — оформим кошелёк по загранпаспорту (от 18 лет): оплата по QR, переводы, такси\n"
                   "▪️ <b>eSIM</b> — подключим интернет, всё работает стабильно и без VPN\n"
                   "▪️ <b>Обмен рублей и USDT → юани</b> — моментально пополним Alipay и WeChat\n\n"
                   ""
                   "Условия:\n"
                   "• Регистрация Alipay — 900₽\n"
                   "🎁 Акция: <b>бесплатно</b> при первом пополнении через наш сервис\n"
                   "• Cимкарта eSIM — от 1500₽\n"
                   "• Пополнение Alipay/WeChat— от 2000 юаней\n\n"
                   ""
                   "<b>С сервисом 2change: </b>\n"
                   "☑️ Не нужен UnionPay — покажем удобные способы оплаты в Китае\n"
                   "☑️ Такси без переплат — научим заказывать самостоятельно\n"
                   "☑️ Интернет без ограничений — работают Telegram, WhatsApp и другие приложения\n\n"
                   ""
                   "<b>👉 Напишите @ALEXANDRA_2CHANGE или оставьте заявку на услугу</b>")

            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("✏️Калькулятор|Оставить заявку", callback_data="calc_cn"))
            kb.add(InlineKeyboardButton("📈Актуальный курс", callback_data="cn_currency_menu"))
            kb.add(InlineKeyboardButton("📲Cимкарта eSIM", callback_data="esim_cn"))
            kb.add(InlineKeyboardButton("💳Регистрация Alipay", callback_data="cn_alipay"))
            kb.add(InlineKeyboardButton("❓Как пополнить Alipay/Wechat", callback_data="cn_faq"))
            kb.add(InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
            send_media("img/cn_main.jpg", chat_id=chat_id, caption=msg, parse_mode="HTML", reply_markup=kb)
        else:
            bot.send_message(chat_id, "<i>Для работы с ботом\n"
                                      "Подпишитесь на 👉  <a href='https://t.me/turkey_2change'>чат 2Change</a></i>",
                             parse_mode="HTML")
    if call.data == "bybit_add":
        msg = ("💳Мы предоставляем услуги по пополнению карт Bybit!\n\n"
               ""
               "<i>📌 Минимальная сумма: 10 000₽</i>\n\n"
               ""
               "<b>Хотите оставить заявку на пополнение?</b>")
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("✅Оставить заявку", callback_data="request/пополнение карты bybit/0"))
        kb.add(InlineKeyboardButton("📋Назад", callback_data="main_menu"))
        bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=kb)


    if call.data == "cn_alipay":
        if check_subscribtion(user_id, 1):
            msg = ("🇨🇳 <b>Онлайн-оформление Alipay для россиян за 5 минут!</b>\n\n"
            "<i>Что такое Alipay?</i>\n"
            "Это китайский электронный кошелёк, который работает <b>без банковской карты</b>.\n\n"
            "<b>С Alipay вы сможете:</b>\n"
            "▪️Оплачивать покупки в магазинах, ресторанах, транспорт, билеты и экскурсии в один клик — весь Китай живёт с Alipay\n"
            "▪️Вызывать такси DiDi прямо в приложении\n"
            "▪️Переводить деньги и принимать оплату\n\n"
            "📲 <b>Как подключаем:</b>\n"
            "1. Вы оставляете заявку\n"
            "2. Мы шаг за шагом помогаем с регистрацией и настройкой\n"
            "3. Пополняете кошелёк через наш сервис — и сразу можете платить в Китае\n\n"
            "⏱️ <b>Вся процедура занимает около 5 минут.</b>\n"
             "Если что-то непонятно — мы всегда на связи.\n\n"
             "🎁 <b>Акция:</b>\n"
            "При первом пополнении через наш сервис оформление Alipay — <b>бесплатно</b>.\n"
            "💳 Без пополнения — стоимость <b>900₽</b>.\n\n"
            "👉🏻 Задайте вопрос — @ALEXANDRA_2CHANGE или оставьте заявку в боте")
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("Оставить заявку✅", callback_data="request/оформление Alipay📋/4"))
            kb.row(InlineKeyboardButton("◀️Назад", callback_data="cn_menu"), InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))


            send_media("img/cn_alipay.jpg", chat_id=chat_id, caption=msg, parse_mode="HTML", reply_markup=kb)
        else:
            bot.send_message(chat_id, "<i>Для работы с ботом\n"
                                      "Подпишитесь на 👉  <a href='https://t.me/turkey_2change'>чат 2Change</a></i>",
                             parse_mode="HTML")
    if call.data == "cn_faq":
        if check_subscribtion(user_id, 1):
            msg = ("💳 <b>Пополнение Alipay или WeChat с российской карты и USDT</b>\n\n"
            "<b>Нельзя пополнить напрямую?</b> Мы сделаем это за вас — <b>быстро и по выгодному курсу</b>.\n\n"
            "<b>Как это работает:</b>\n"
            "• Оставляете заявку в боте\n"
            "• Переводите рубли или USDT\n"
            "• Присылаете номер своего кошелька или QR-код\n"
            "• Моментально получаете юани\n\n"
            "🔁 <b>Вы можете также обменять ваши юани на рубли</b>\n\n"
            "✔️ <b>Комиссия: 0%</b>\n"
            "✔️ <b>Мин. сумма: 2 000 юаней</b>\n"
            "✔️ <b>Гарантия возврата, если не получите перевод за 1 час</b>\n\n"
            "➡️ Пишите @ALEXANDRA_2CHANGE или оставьте заявку в боте")

            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("Оставить заявку✅", callback_data="request/пополнение Alipay💰/4"))
            kb.row(InlineKeyboardButton("◀️Назад", callback_data="cn_menu"),
                   InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
            send_media("img/cn_ap_wc.jpg", chat_id=chat_id, caption=msg, parse_mode="HTML", reply_markup=kb)
        else:
            bot.send_message(chat_id, "<i>Для работы с ботом\n"
                                      "Подпишитесь на 👉  <a href='https://t.me/turkey_2change'>чат 2Change</a></i>",
                             parse_mode="HTML")

    if call.data == "kr_menu":
        if check_subscribtion(user_id, 5):
            if chat_id in user_calc_states:
                del user_calc_states[chat_id]
            msg = ("<b>🇰🇷2Change - услуги в Корее</b>\n\n"
                   ""
                   "🕓График работы:\n"
                   "Пн-Сб 10:00 - 20:00 (Вс - выходной)")

            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("✏️Калькулятор|Оставить заявку", callback_data="calc_kr"))
            kb.add(InlineKeyboardButton("📈Актуальный курс", callback_data="kr_currency_menu"))
            kb.add(InlineKeyboardButton("🎁Бесплатная симкарта eSIM", callback_data="esim_kr"))
            kb.row(InlineKeyboardButton("Наличные воны🏧", callback_data="kr_cash_transactions_menu"), InlineKeyboardButton("Оплата обучения📚", callback_data="kr_edu"))
            kb.add(InlineKeyboardButton("Зарубежная карта💳", callback_data="tr_card_menu"))
            kb.add(InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
            bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=kb)
        else:
            bot.send_message(chat_id, "<i>Для работы с ботом\n"
                                      "Подпишитесь на 👉  <a href='https://t.me/korea_obmen1'>чат 2Change</a></i>",
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

        if call.data == "esim_main":
            if check_subscribtion(user_id, 5):
                if chat_id in to_edit:
                    del to_edit[chat_id]
                msg = ("<b>Боитесь остаться без связи в чужой стране?</b>\n"
                        "Роуминг дорогой, а местные симки — сплошная суета?\n"
                        "<i>📲 Подключите eSIM с интернетом еще до вылета — быстро, удобно и с поддержкой на каждом шаге!</i>\n\n"
                         ""
                        "💡 Условия:\n"
                       "✔️ Быстрое подключение\n"
                       "✔️ Интернет <b><i>без визита в салон</i></b>\n"
                       "✔️ Для каждой страны свои тарифы\n\n"
                       ""
                       "<b>📌 Часто задаваемые вопросы:</b>\n\n"
                       "• Что такое eSIM? \n"
                       "Электронная симкарта, встроенная в большинство современных смартфонов.\n\n"
                       ""
                       "• Как подключить eSIM?\n"
                       "Сканируете QR-код → eSIM подключается → перед вылетом или уже по прилету в страну включаете eSIM и пользуетесь интерентом.\n\n"
                       ""
                       "<b>• Совместимость</b>\n"
                       "— <b>iPhone:</b> Настройки → Сотовая связь → «Добавить eSIM»\n"
                       "— <b>Android:</b> Настройки → Подключения / Сеть и интернет → Диспетчер SIM-карт → «Добавить eSIM»\n\n"
                       "<i>👇 Выберите страну или напишите менеджеру @ALEXANDRA_2CHANGE 👩🏻‍💼</i>")
                keyboard = InlineKeyboardMarkup()
                keyboard.row(InlineKeyboardButton("🇹🇷Турция", callback_data="esim_tr"), InlineKeyboardButton("🇹🇭Тайланд", callback_data="esim_thai"))
                keyboard.row(InlineKeyboardButton("🇨🇳Китай", callback_data="esim_cn"), InlineKeyboardButton("🇰🇷Корея", callback_data="esim_kr"))
                keyboard.add(InlineKeyboardButton("🇦🇪ОАЭ (Дубай)", callback_data="esim_ae"))
                keyboard.add(InlineKeyboardButton("📋Главное меню", callback_data="main_menu"))
                send_media("img/esimmain.jpg", chat_id, msg, reply_markup=keyboard)
            else:
                bot.send_message(chat_id, "<i>Для работы с ботом\n"
                                          "Подпишитесь на 👉  <a href='https://t.me/korea_obmen1'>чат 2Change</a></i>",
                                 parse_mode="HTML")
        elif call.data == "esim_kr":
            if check_subscribtion(user_id, 5):
                key = InlineKeyboardMarkup()
                msg= ("<b>📲Хотите оставаться на связи в Корее?</b>\n"
                      "<i>Подключите eSIM с интернетом еще до вылета - быстро, удобно и с поддержкой на каждому шагу!</i>\n\n"
                      ""
                      "<b>💡Что вы получите?</b>\n"
                      "✔️Бесплатное подключение\n"
                      "✔️Интернет на 30 дней\n"
                      "✔️Связь сразу по прилете - <i>без визита в салон</i>\n"
                      "🎁<i>При обмене от 2 000 000 ₩ - eSIM + 3Гб интернета в подарок!</i>\n\n"
                      ""
                      "<b>💰Тарифы на 30 дней:</b>\n"
                      "🇰🇷5 ГБ - 1 600₽\n"
                      "🇰🇷10 ГБ - 3 000₽\n"
                      "🇰🇷20 ГБ - 6 000₽\n"
                      "🇰🇷50 ГБ - 12 000₽\n"
                      "<b>♾Безлимитный интернет</b> - 14 000₽\n\n"
                      ""
                      "<b>Оставьте заявку или напишите менеджеру @ALEXANDRA_2CHANGE</b>👩🏻‍")
                key.row(InlineKeyboardButton("←", callback_data="esim_faq/5"), InlineKeyboardButton(text="1/2", callback_data="ignore"), InlineKeyboardButton("→", callback_data="esim_faq/5"))
                key.add(InlineKeyboardButton("Оставить заявку на eSIM✅", callback_data="request/📲получить eSIM/5"))
                key.add(InlineKeyboardButton("Другие страны🌏", callback_data="esim_main"))
                if chat_id not in to_edit:
                    if "img/esimmain.jpg" in img_cache:
                        sent= bot.send_photo(chat_id, caption=msg, photo=img_cache["img/esimmain.jpg"], reply_markup=key, parse_mode="html")
                        to_edit[chat_id] = sent.message_id
                    else:
                        with open("img/esimmain.jpg", "rb") as media:
                            sent = bot.send_photo(chat_id, media, caption=msg, reply_markup=key, parse_mode="HTML")
                            img_cache["img/esimmain.jpg"] = sent.photo[-1].file_id
                            to_edit[chat_id] = sent.message_id
                else:
                    msg_id = to_edit[chat_id]
                    bot.edit_message_caption(msg,chat_id,parse_mode="HTML",message_id=msg_id,reply_markup=key)
            else:
                bot.send_message(chat_id, "<i>Для работы с ботом\n"
                                          "Подпишитесь на 👉  <a href='https://t.me/korea_obmen1'>чат 2Change</a></i>",
                                 parse_mode="HTML")

        elif call.data == "esim_thai":
            if check_subscribtion(user_id, 5):
                key = InlineKeyboardMarkup()
                key.row(InlineKeyboardButton("←", callback_data="esim_faq/3"), InlineKeyboardButton(text="1/2", callback_data="ignore"),
                        InlineKeyboardButton("→", callback_data="esim_faq/3"))
                key.add(InlineKeyboardButton("Оставить заявку на eSIM✅", callback_data="request/📲получить eSIM/3"))
                key.add(InlineKeyboardButton("Другие страны🌏", callback_data="esim_main"))
                msg= ("<b>📲Хотите оставаться на связи в Тайланде?</b>\n"
                      "<i>Подключите eSIM с интернетом еще до вылета - быстро, удобно и с поддержкой на каждому шагу!</i>\n\n"
                      ""
                      "<b>💡Что вы получите?</b>\n"
                      "✔️Бесплатное подключение\n"
                      "✔️Интернет на 30 дней\n"
                      "✔️Связь сразу по прилете - <b>без визита в салон</b>\n\n"
                      
                      ""
                      "<b>💰Тарифы на 30 дней:</b>\n"
                      "🇹🇭1 ГБ - 400₽\n"
                      "🇹🇭3 ГБ - 800₽\n"
                      "🇹🇭5 ГБ - 1 100₽\n"
                      "🇹🇭10 ГБ - 1 800₽\n\n"
                      
                      ""
                      "<b>Оставьте заявку или напишите менеджеру @ALEXANDRA_2CHANGE</b>👩🏻‍")

                if chat_id not in to_edit:
                    if "img/esimmain.jpg" in img_cache:
                        sent = bot.send_photo(chat_id, caption=msg, photo=img_cache["img/esimmain.jpg"], reply_markup=key,
                                              parse_mode="html")
                        to_edit[chat_id] = sent.message_id
                    else:
                        with open("img/esimmain.jpg", "rb") as media:
                            sent = bot.send_photo(chat_id, media, caption=msg, reply_markup=key, parse_mode="HTML")
                            img_cache["img/esimmain.jpg"] = sent.photo[-1].file_id
                            to_edit[chat_id] = sent.message_id
                else:
                    msg_id = to_edit[chat_id]
                    bot.edit_message_caption(msg, chat_id, parse_mode="HTML", message_id=msg_id, reply_markup=key)
            else:

                bot.send_message(chat_id, "<i>Для работы с ботом\n"
                                          "Подпишитесь на 👉  <a href='https://t.me/korea_obmen1'>чат 2Change</a></i>",
                                 parse_mode="HTML")
        elif call.data == "esim_cn":
            if check_subscribtion(user_id, 5):
                key = InlineKeyboardMarkup()
                key.row(InlineKeyboardButton("←", callback_data="esim_faq/4"), InlineKeyboardButton(text="1/2", callback_data="ignore"),
                        InlineKeyboardButton("→", callback_data="esim_faq/4"))
                key.add(InlineKeyboardButton("Оставить заявку на eSIM✅", callback_data="request/📲получить eSIM/4"))
                key.add(InlineKeyboardButton("Другие страны🌏", callback_data="esim_main"))
                msg = ("<b>📲Хотите оставаться на связи в Китае?</b>\n"
                       "<i>Подключите eSIM с интернетом еще до вылета - быстро, удобно и с поддержкой на каждому шагу!</i>\n\n"
                       ""
                       "<b>💡Что вы получите?</b>\n"
                       "✔️Бесплатное подключение\n"
                       "✔️Интернет на 30 дней\n"
                       "✔️Связь сразу по прилете - <b>без визита в салон</b>\n"
                       "✔️Работают даже заблокированные приложения в Китае!\n\n"
    
                       ""
                       "<b>💰Тарифы на 30 дней:</b>\n"
                       "🇨🇳1 ГБ - 450₽\n"
                       "🇨🇳3 ГБ - 900₽\n"
                       "🇨🇳5 ГБ - 1 250₽\n"
                       "🇨🇳10 ГБ - 1 800₽\n\n"
    
                       ""
                       "<b>Оставьте заявку или напишите менеджеру @ALEXANDRA_2CHANGE</b>👩🏻‍")

                if chat_id not in to_edit:
                    if "img/esimmain.jpg" in img_cache:
                        sent = bot.send_photo(chat_id, caption=msg, photo=img_cache["img/esimmain.jpg"], reply_markup=key,
                                              parse_mode="html")
                        to_edit[chat_id] = sent.message_id
                    else:
                        with open("img/esimmain.jpg", "rb") as media:
                            sent = bot.send_photo(chat_id, media, caption=msg, reply_markup=key, parse_mode="HTML")
                            img_cache["img/esimmain.jpg"] = sent.photo[-1].file_id
                            to_edit[chat_id] = sent.message_id
                else:
                    msg_id = to_edit[chat_id]
                    bot.edit_message_caption(msg, chat_id, parse_mode="HTML", message_id=msg_id, reply_markup=key)
            else:

                bot.send_message(chat_id, "<i>Для работы с ботом\n"
                                          "Подпишитесь на 👉  <a href='https://t.me/korea_obmen1'>чат 2Change</a></i>",
                                 parse_mode="HTML")
        elif call.data == "esim_ae":
            if check_subscribtion(user_id, 5):
                key = InlineKeyboardMarkup()
                key.row(InlineKeyboardButton("←", callback_data="esim_faq/6"), InlineKeyboardButton(text="1/2", callback_data="ignore"),
                        InlineKeyboardButton("→", callback_data="esim_faq/6"))
                key.add(InlineKeyboardButton("Оставить заявку на eSIM✅", callback_data="request/📲получить eSIM/6"))
                key.add(InlineKeyboardButton("Другие страны🌏", callback_data="esim_main"))
                msg = ("<b>📲Хотите оставаться на связи в ОАЭ?</b>\n"
                       "<i>Подключите eSIM с интернетом еще до вылета - быстро, удобно и с поддержкой на каждому шагу!</i>\n\n"
                       ""
                       "<b>💡Что вы получите?</b>\n"
                       "✔️Бесплатное подключение\n"
                       "✔️Интернет на 30 дней\n"
                       "✔️Связь сразу по прилете - <b>без визита в салон</b>\n\n"
    
                       ""
                       "<b>💰Тарифы на 30 дней:</b>\n"
                       "🇦🇪1 ГБ - 1 300₽\n"
                       "🇦🇪3 ГБ - 3 500₽\n"
                       "🇦🇪5 ГБ - 5 000₽\n"
                       "🇦🇪10 ГБ - 8 500₽\n\n"
    
                       ""
                       "<b>Оставьте заявку или напишите менеджеру @ALEXANDRA_2CHANGE</b>👩🏻‍")

                if chat_id not in to_edit:
                    if "img/esimmain.jpg" in img_cache:
                        sent = bot.send_photo(chat_id, caption=msg, photo=img_cache["img/esimmain.jpg"], reply_markup=key,
                                              parse_mode="html")
                        to_edit[chat_id] = sent.message_id
                    else:
                        with open("img/esimmain.jpg", "rb") as media:
                            sent = bot.send_photo(chat_id, media, caption=msg, reply_markup=key, parse_mode="HTML")
                            img_cache["img/esimmain.jpg"] = sent.photo[-1].file_id
                            to_edit[chat_id] = sent.message_id
                else:
                    msg_id = to_edit[chat_id]
                    bot.edit_message_caption(msg, chat_id, parse_mode="HTML", message_id=msg_id, reply_markup=key)
            else:
                bot.send_message(chat_id, "<i>Для работы с ботом\n"
                                          "Подпишитесь на 👉  <a href='https://t.me/korea_obmen1'>чат 2Change</a></i>",
                                 parse_mode="HTML")

        elif call.data == "esim_tr":
            if check_subscribtion(user_id, 1):
                key = InlineKeyboardMarkup()
                key.row(InlineKeyboardButton("←", callback_data="esim_faq/1"), InlineKeyboardButton(text="1/2", callback_data="ignore"),
                        InlineKeyboardButton("→", callback_data="esim_faq/1"))
                key.add(InlineKeyboardButton("Оставить заявку на eSIM✅", callback_data="request/📲получить eSIM/1"))
                key.add(InlineKeyboardButton("Другие страны🌏", callback_data="esim_main"))
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
                    "✔️ Выгодное пополнение при необходимости\n\n"
                    "🇹🇷 <b>5 ГБ — 1900₽</b>\n"
                    "🇹🇷 <b>10 ГБ — 2500₽</b>\n"
                    "🇹🇷 <b>20 ГБ — 3300₽</b>\n\n"
                    "🎁 <b>Бонус +10 ГБ трафика в подарок</b>, при обмене от 20 000 лир через QR!\n\n"
                    "👇 <b>Оставьте заявку</b> или напишите менеджеру\n "
                    "@ALEXANDRA_2CHANGE 👩🏻‍💼"
                )
                if chat_id not in to_edit:
                    if "img/esimmain.jpg" in img_cache:
                        sent = bot.send_photo(chat_id, caption=msg, photo=img_cache["img/esimmain.jpg"], reply_markup=key,
                                              parse_mode="html")
                        to_edit[chat_id] = sent.message_id
                    else:
                        with open("img/esimmain.jpg", "rb") as media:
                            sent = bot.send_photo(chat_id, media, caption=msg, reply_markup=key, parse_mode="HTML")
                            img_cache["img/esimmain.jpg"] = sent.photo[-1].file_id
                            to_edit[chat_id] = sent.message_id
                else:
                    msg_id = to_edit[chat_id]
                    bot.edit_message_caption(msg, chat_id, parse_mode="HTML", message_id=msg_id, reply_markup=key)
            else:
                bot.send_message(chat_id, "<i>Для работы с ботом\n"
                                          "Подпишитесь на 👉  <a href='https://t.me/turkey_2change'>чат 2Change</a></i>",
                                 parse_mode="HTML")
        elif call.data.startswith("esim_faq/"):
            _, country = call.data.split("/")
            esim_countries = {
                "1": "esim_tr",  # Турция
                "3": "esim_thai",  # Тайланд
                "4": "esim_cn",  # Китай
                "5": "esim_kr",  # Корея
                "6": "esim_ae"  # ОАЭ
            }
            key = InlineKeyboardMarkup()
            key.row(InlineKeyboardButton("←", callback_data=f"{esim_countries[country]}"), InlineKeyboardButton(text="2/2", callback_data="ignore"),
                    InlineKeyboardButton("→", callback_data=f"{esim_countries[country]}"))
            key.add(InlineKeyboardButton("Оставить заявку на eSIM✅", callback_data=f"request/📲получить eSIM/{country}"))
            key.add(InlineKeyboardButton("Другие страны🌏", callback_data="esim_main"))
            msg = ("Часто задаваемые вопросы:\n\n"
                   ""
                   "<b>• Что такое eSIM?</b>\n"
                   "Это электронная симкарта, встроенная в современные смартфоны, большинство айфонов от 11 модели поддерживают eSIM.\n\n"
                   ""
                   "<b>• Как подключить eSIM?</b>\n"
                   "Сканируйте QR-код - телефон активирует eSIM, интернет заработает.\n\n"
                   ""
                   "<b>• Совместимость</b>\n"
                   "— <b>iPhone:</b> Настройки → Сотовая связь → «Добавить eSIM»\n"
                   "— <b>Android:</b> Настройки → Подключения / Сеть и интернет → Диспетчер SIM-карт → «Добавить eSIM»\n\n"
                   ""
                   "<b>• Как это работает по шагам</b>\n"
                   "Сканируете QR→ eSIM подключается → перед вылетом или уже в стране включаете и пользуетесь.\n\n"
                   ""
                   "<i>👇Оставьте заявку или напишите менеджеру @ALEXANDRA_2CHANGE🦸🏻‍♀️</i>")
            if chat_id not in to_edit:
                if "img/esimmain.jpg" in img_cache:
                    sent = bot.send_photo(chat_id, caption=msg, photo=img_cache["img/esimmain.jpg"], reply_markup=key,
                                          parse_mode="html")
                    to_edit[chat_id] = sent.message_id
                else:
                    with open("img/esimmain.jpg", "rb") as media:
                        sent = bot.send_photo(chat_id, media, caption=msg, reply_markup=key, parse_mode="HTML")
                        img_cache["img/esimmain.jpg"] = sent.photo[-1].file_id
                        to_edit[chat_id] = sent.message_id
            else:
                msg_id = to_edit[chat_id]
                bot.edit_message_caption(msg, chat_id, parse_mode="HTML", message_id=msg_id, reply_markup=key)








    #МЕНЮ ТУРЦИИ
    if call.data=="tr_card_menu":
        if check_subscribtion(user_id, 1):
            photo_path = "img/card_video.mp4"
            msg =("💳 Друзья, есть возможность выпустить зарубежную карту <b>Bybit Card — доставим физическую карту</b> по России за 2 недели, а виртуальной можно оплачивать покупки в интернете уже через 10 минут! \n\n"
                  ""
                  "<b>Преимущества:</b> \n"
                  "💰 Лимиты: до 5 000 $ в сутки и 50 000 $ в месяц.\n"
                  "💳 Форматы: виртуальная и/или пластиковая карта.\n"
                  "📦 Доставка в Россию — за 2 недели курьером прямо к двери.\n\n"
                  ""
                  "Санкции ужесточаются и оформить карту позже может стать сложнее.\n\n"
                  ""
                  "👉Напишите @ALEXANDRA_2CHANGE или оставьте заявку, чтобы узнать подробности")
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("Оставить заявку✅", callback_data="request/💳зарубежная карта/0"))
            keyboard.add(InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
            send_media(photo_path, chat_id, msg, keyboard, parse_mode="HTML")
        else:
            bot.send_message(chat_id, "<i>Для работы с ботом\n"
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
    if call.data=="tr_currency_menu": #ТУРЦИЯ
        finstr = FinInstr()
        msg = finstr.show_currency(country=1)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✏️Рассчитать сумму", callback_data="calc_tr"))
        keyboard.add(InlineKeyboardButton("❔Задать вопрос", callback_data="request/❔вопрос про курсы валют/1"))
        bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)
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

    if call.data == "cn_currency_menu":
        finstr = FinInstr()
        msg = finstr.show_currency(country=4)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✏️Рассчитать сумму", callback_data="calc_cn"))
        keyboard.add(InlineKeyboardButton("💳Зарубежная карта", callback_data="tr_card_menu"))
        keyboard.add(InlineKeyboardButton("❔Задать вопрос", callback_data="request/❔вопрос про курсы валют/4"))
        bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)

    #МЕНЮ КОРЕИ
    if call.data == "kr_currency_menu":

        finstr = FinInstr()
        msg = finstr.show_currency(country=5)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✏️Рассчитать сумму", callback_data="calc_kr"))
        keyboard.add(InlineKeyboardButton("❔Задать вопрос", callback_data="request/❔вопрос про курсы валют/5"))
        bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)
    if call.data== "kr_cash_transactions_menu":
        msg = ("💵 Как обменять рубли и USDT на наличные воны — за 5 минут в любом городе Южной Кореи! 🏧 🏧\n\n"
               ""
               "Получите наличные воны без карты в любом банкомате по QR-коду — даже в аэропорту. Рядом с магазинами 7-Eleven и CU.\n\n"
               ""
               "▪️ Лимиты: от 300 000₩ до 20 млн ₩\n"
               "▪️ Комиссия: 0%\n"
               "▪️ Требования: телефон с интернетом (подключить eSIM)\n"
               "🎁 eSIM +3 ГБ в подарок при обмене от 2 000 000₩ !\n\n"
               ""
               "🔄 Как это работает:\n"
               "— Оставьте заявку в боте или напишите @ALEXANDRA_2CHANGE\n"
               "— Переведите рубли или USDT\n"
               "— Отправьте нам фото QR-кода на экране банкомата\n"
               "— Заберите наличные воны\n"
               "Смотрите простую инструкцию в коротком видео!\n\n"
               "👇 Рассчитайте обмен или напишите менеджеру\n"
               " @ALEXANDRA_2CHANGE")
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("📈Курсы|Калькулятор", callback_data="kr_currency_menu"))
        kb.add(InlineKeyboardButton("🎁Бесплатная симкарта eSIM", callback_data="esim_kr"))
        kb.row(InlineKeyboardButton("◀️Назад", callback_data="kr_menu"), InlineKeyboardButton("📋Главное меню", callback_data="main_menu"))
        send_media("img/krw_cash.MP4", chat_id=chat_id, caption=msg, reply_markup=kb, parse_mode="HTML")
    if call.data== "kr_edu":
        msg = ("🇰🇷 Хотите оплатить учёбу в Южной Корее?\n"
               "Оплатим языковые курсы, университеты и колледжи напрямую — с поддержкой, без поездок и лишних сложностей.\n\n"
               ""
               "Как это работает:\n"
               "1. Вы переводите нам рубли или USDT.\n"
               "2. Мы оплачиваем ваш инвойс с корейского банка.\n"
               "3. Деньги зачисляются в вонах на счёт учебного заведения\n"
               "Удобно для студентов и их родителей. Быстро и безопасно.\n\n"
               ""
               "📌 Для каждого клиента оптимальные условия и курс — в зависимости от задачи.\n\n"
               ""
               "👉 Оставьте заявку в боте или напишите менеджеру @ALEXANDRA_2CHANGE — расскажем подробнее и поможем с оплатой.")
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("📈Курсы|Калькулятор", callback_data="kr_currency_menu"))

        kb.row(InlineKeyboardButton("◀️Назад", callback_data="kr_menu"),
               InlineKeyboardButton("📋Главное меню", callback_data="main_menu"))
        send_media("img/kr_edu_pic.jpg", chat_id, msg, reply_markup=kb, parse_mode="HTML")


    #ТЕХНИЧЕСКИЕ ЛОВЦЫ
    if call.data.startswith("request/"):
        _, request, country= call.data.split("/")
        send_application(user_id=user_id, user_name=user_name, user_ref=user_ref, chat_id=chat_id,country=int(country),reason=request)
        if chat_id in to_edit:
            del to_edit[chat_id]
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
                   "cny/rub":"<b>300 CNY</b>",
                   "usd/krw": "<b>214 USDT</b>",
                   "krw/usd":"<b>300.000 KRW</b>",
                   "rub/krw":"<b>17302 RUB</b>",
                   "krw/rub":"<b>300.000 KRW</b>"}

        countries_menu = {"1":"tr_menu", "2":"rf_menu", "3":"thai_menu", "4":"cn_menu", "5":"kr_menu"}
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
            keybord1.row(InlineKeyboardButton("💰Иные валюты (менеджер)", callback_data="request/💰Обмен иных валют/2"),
                        InlineKeyboardButton("◀️Назад", callback_data="rf_menu"))
            bot.send_message(chat_id, msg, reply_markup=keybord1, parse_mode="HTML")
        elif call.data == "calc_thai":
            msg = "💸<i>Выберите валюту для обмена:</i>"
            keybord2 = InlineKeyboardMarkup(row_width=2)
            keybord2.row(InlineKeyboardButton("🪙USDT→🇹🇭 (Переводом)", callback_data="exchange/usd/thb/3"),
                        InlineKeyboardButton("🪙USDT→🇹🇭 (Наличные)", callback_data="exchange/usd/thb_cash/3"))

            keybord2.row(InlineKeyboardButton("🇷🇺→🇹🇭 (Переводом)", callback_data="exchange/rub/thb/3"),
                        InlineKeyboardButton("🇷🇺→🇹🇭 (Наличные)", callback_data="exchange/rub/thb_cash/3"))
            keybord2.row(InlineKeyboardButton("💰Иные валюты (менеджер)", callback_data="request/💰Обмен иных валют/3"),
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
            keybord4.add(InlineKeyboardButton("🇨🇳CNY (юань)→🇷🇺", callback_data="exchange/cny/rub/4"))
            keybord4.row(InlineKeyboardButton("💰Иные валюты (менеджер)", callback_data="request/💰Обмен иных валют/4"),
                         InlineKeyboardButton("◀️Назад", callback_data="cn_menu"))
            bot.send_message(chat_id, msg, reply_markup=keybord4, parse_mode="HTML")
        elif call.data == "calc_kr":
            msg = ("<i>Выберите валюту для обмена:</i>\n\n"
                   "<b>🎁 При обмене от 2 000 000₩ – eSIM +3 ГБ в подарок!</b>")
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("🇰🇷 KRW (нал/перевод) → 🇷🇺RUB", callback_data="exchange/krw/rub/5"))
            kb.add(InlineKeyboardButton("🇰🇷 KRW (нал/перевод) → 🪙 USDT", callback_data="exchange/krw/usd/5"))
            kb.add(InlineKeyboardButton("🇷🇺RUB → 🇰🇷 KRW (нал/счет)", callback_data="exchange/rub/krw/5"))
            kb.add(InlineKeyboardButton("🪙 USDT → 🇰🇷 KRW (нал/счет)", callback_data="exchange/usd/krw/5"))
            kb.row(InlineKeyboardButton("💰Иные валюты (менеджер)", callback_data="request/💰Обмен иных валют/5"),
                         InlineKeyboardButton("◀️Назад", callback_data="kr_menu"))
            bot.send_message(chat_id, msg, reply_markup=kb, parse_mode="HTML")

    if call.data.startswith("apq"):
        _, verdict, tg_id= call.data.split("/")
        _, tg_id, country, client_name, amount1, amount2, currency1, currency2, reason, created_at = qdb.get_from_queue(get_by_id=tg_id)
        if verdict == "y":
            keyboard= InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("💬Связаться с клиентом", callback_data="contact_client"))
            apmake = ApplicationCreator(country=country, client_name=client_name,reason=reason,currency1=currency1, currency2=currency2, amount1=amount1, amount2=amount2, time=created_at)
            msg = apmake.create()
            sent_msg = bot.send_message(manager_chat_id, msg, parse_mode="HTML", reply_markup=keyboard)
            if qdb.set_user_name(sent_msg.message_id, user_id, user_ref):
                bot.send_message(tg_id, "✅Заявка подтверждена, менеджер ответит вам в ближайшее время!")
            else:
                bot.send_message(chat_id, "⛔️Менеджер не сможет вам написать из-за ваших настроек приватности⛔️\n "
                                          "Включите видимость вашего аккаунта по ссылке в настройках приватности, или напишите @ALEXANDRA_2CHANGE",
                                 parse_mode="HTML")

        if verdict == "n":
            bot.send_message(tg_id, "❌Заявка отменена")
    if call.data.startswith("chc"):
        _, table_name= call.data.split("/")
        admin_change_coef_states[chat_id] = table_name
        bot.send_message(chat_id,text="✏️Введите новую наценку в процентах в формате десятичной дроби (1.0 = 1%; 1.5=1.5%):\n\n"
                         "<i>Число не должно быть меньше 0</i>\n", parse_mode="HTML")
        bot.register_next_step_handler(call.message, process_coef_change)
    if call.data == "convert":
        app_state= user_calc_states.get(chat_id, {})
        currency1, currency2,country, amount1, amount2 = app_state["currency1"],app_state["currency2"],app_state["country"],app_state["amount1"],app_state["amount2"]


        send_application(user_id=user_id, user_name=user_name, user_ref=user_ref, chat_id=chat_id,amount1=amount1,amount2=amount2, country=country, currency1=currency_names[currency1], currency2=currency_names[currency2])
        del user_calc_states[chat_id]
        logger.info(f"Удалено состояние чата {chat_id}!!!")
    if call.data == "contact_client": #ВОТ ЭТУ ХУЙНЮ НАДО ЗАСУНУТЬ В БАЗУ ДАННЫХ А ТО ПИЗДЕЦ

        _, client_id, client_ref = qdb.get_user_name(message_id)
        if client_id or client_ref:
            new_text = call.message.text + "\n" + f"\n✅<b>Взят в работу:</b>\n<i>{datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}</i>\n\n💼Менеджер: {user_name} " + "\n" + f"\n<a href='tg://user?id={client_id}'>👉Cсылка на чат с клиентом👈</a> {f"@{client_ref}" if client_ref else ""}"
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text, parse_mode="HTML", reply_markup=None)
            logger.info(f"[ЗАЯВКА ВЗЯТА] Менеджер {user_name} взял заявку клиента {client_ref if client_ref else client_id}  в {datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")} ")
        else:
            new_text = call.message.text + "\n" + f"\n✅<b>Взят в работу:</b>\n<i>{datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}</i>\n\n💼Менеджер: {user_name} " + "\n" + f"\n<b>⚠️НЕТ ССЫЛКИ! У клиента отключен доступ к профилю по ссылке и отсутствует юзернейм. Клиенту был отправлен юзернейм менеджера⚠️</b>"
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text, parse_mode="HTML",
                                  reply_markup=None)


















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
                  "cny/rub": 300,
                  "krw/rub": 300000,
                  "krw/usd": 300000,
                  "usd/krw": 214,
                  "rub/krw": 17302}
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
           f"<b>Вы получаете:</b> {converted} {currency_names[currency2]}\n"
           f"<b>Курс: {float(message.text) / float(converted) if float(converted) < float(message.text) else float(converted)/float(message.text):.2f}</b>\n"
           f"<b>Курс актуален в течении 15 минут!</b>\n\n"
           f"<b>Отправить заявку на обмен?</b>")
    user_calc_states[chat_id]["amount1"]=int(message.text)
    user_calc_states[chat_id]["amount2"]=converted

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
        bot.send_message(chat_id, "✅Наценка изменена! Изменения появятся в течении 5 минут.")

    except Exception as e:
        bot.send_message(chat_id, f"Что-то пошло не так, уведомили программиста:\n\n"
                                  f"{e}")




