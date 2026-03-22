import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime, time

from config import BOT_TOKEN, TEST_BOT_TOKEN, ADMIN_IDS, NOTIFICATION_CHAT, TEST_NOTIFICATION_CHAT, TEST_MODE, SUPPORT_CHAT_ID
from utils import logger,  day_off
from database_main import QueueDB
from converter import FinInstr

from services.subscription import SubscriptionService
from services.applications import ApplicationCreator
from services.senders import SenderService
from services.exchange_service import ExchangeService
from services.state_manager import StateManager

from handlers.turkey import TurkeyHandlers
from handlers.korea import KoreaHandlers
from handlers.esim import EsimHandlers
from handlers.china import ChinaHandlers
from handlers.russia import RussiaHandlers
from handlers.thailand import ThailandHandlers
from handlers.vietnam import VietnamHandlers


#глобали
img_cache={}



admin_change_coef_states= {}
to_edit= {}


manager_chat_id = NOTIFICATION_CHAT if not TEST_MODE else TEST_NOTIFICATION_CHAT




class MyExceptionHandler(telebot.ExceptionHandler):

    def handle(self, exception):
        # Игнорируем ошибки, которые пришли от Telegram API
        if isinstance(exception, telebot.apihelper.ApiTelegramException):
            # Можно залогировать для отладки, но не слать в support
            logger.warning(f"Ignored Telegram API exception: {exception}")
            return False  # возвращаем False, чтобы бот не считал это обработанной критической ошибкой

        # Для всех остальных ошибок — логируем и шлем в SUPPORT_CHAT
        message = f"Ошибка в боте: {exception}"
        logger.error(message, exc_info=True)
        bot.send_message(SUPPORT_CHAT_ID, message)
        return True


qdb=QueueDB()

bot = telebot.TeleBot(BOT_TOKEN if not TEST_MODE else TEST_BOT_TOKEN, exception_handler=MyExceptionHandler())
finstr = FinInstr()

subscription_service = SubscriptionService(bot, logger, TEST_MODE)


sender_service = SenderService(bot, qdb, manager_chat_id, day_off)

state_manager = StateManager(logger)
exchange_service = ExchangeService(bot, logger, sender_service, FinInstr, state_manager)
exchange_service.register_handlers()


turkey_handlers = TurkeyHandlers(
    bot,
    subscription_service,
    sender_service.send_media,
    finstr,
    state_manager
)
turkey_handlers.register()


russia_handlers = RussiaHandlers(
    bot,
    subscription_service,
    sender_service.send_media,
    finstr,
    state_manager,
)
russia_handlers.register()


korea_handlers = KoreaHandlers(
    bot,
    subscription_service,
    sender_service.send_media,
    finstr,
    state_manager,
)
korea_handlers.register()


thailand_handlers = ThailandHandlers(
    bot,
    subscription_service,
    sender_service.send_media,
    finstr,
    state_manager,
)
thailand_handlers.register()
china_handlers = ChinaHandlers(
    bot,
    subscription_service,
    sender_service.send_media,
    finstr,
    state_manager,
)
china_handlers.register()


esim_handlers = EsimHandlers(
    bot,
    subscription_service,
    sender_service,
    state_manager,

)
esim_handlers.register()

vietnam_handlers = VietnamHandlers(
    bot,
    subscription_service,
    sender_service.send_media,
    finstr,
    state_manager,
)
vietnam_handlers.register()















@bot.message_handler(commands=['start'])
def handle_start(message, not_first:bool=None):

    state_manager.clear(message.chat.id)
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1= InlineKeyboardButton( "🇹🇷 Турция", callback_data="tr_menu")
    button2 = InlineKeyboardButton("🇹🇭 Тайланд", callback_data="thai_menu")
    keyboard.row(button1, button2)
    keyboard.row(InlineKeyboardButton("🇨🇳Китай", callback_data="cn_menu"), InlineKeyboardButton("🇰🇷Корея", callback_data="kr_menu"))

    keyboard.add(InlineKeyboardButton("🇷🇺 Россия (USDT)", callback_data="rf_menu"))
    keyboard.add(InlineKeyboardButton("🇻🇳 Вьетнам", callback_data="vn_menu"))
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

    sender_service.send_media(path=video_path,chat_id=message.chat.id,reply_markup=keyboard,caption=msg)

@bot.message_handler(commands=['manager'])
def handle_manager(message):
    state_manager.clear(message.chat.id)
    last_name = message.from_user.last_name or ""
    user_name = (message.from_user.first_name or "") + (" " + last_name if last_name else "")
    user_id = message.from_user.id
    user_ref = message.from_user.username

    if day_off():
        qdb.add_to_queue(tg_id=user_id, name=user_name, reason="🔔вызов менеджера")
        msg = ("🏄‍♂️<b>К СОЖАЛЕНИЮ, МЫ СЕЙЧАС НЕ РАБОТАЕМ</b>🏄‍♀️\n\n"
               "✅Добавили вашу заявку в очередь\n\n"
               "⚡️В <b>рабочее</b> время менеджер получит вашу заявку и свяжется с вами\n"
               "🕰<b>Наш график работы:</b>\n"
               "Пн-Сб: 10:00 - 20:00\n"
               "Воскресенье:\n"
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
                       "Воскресенье:\n"
                       "<b>выходной</b>", parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, "⛔️Менеджер не сможет вам написать из-за ваших настроек приватности⛔️\n "
                                      "Включите видимость вашего аккаунта по ссылке в настройках приватности, или напишите @ALEXANDRA_2CHANGE",
                             parse_mode="HTML")






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
@bot.message_handler(commands=['change_coef'], func=lambda message: message.from_user.id in ADMIN_IDS)# func=lambda message: message.from_user.id in admin_id)
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




@bot.callback_query_handler(func=lambda c: c.data == "main_menu")
def handle_main_menu(call):
    bot.answer_callback_query(call.id)
    handle_start(call.message, True)





@bot.callback_query_handler(func=lambda c: c.data.startswith("request/"))
def handle_request(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    user_ref = call.from_user.username
    chat_id = call.message.chat.id
    last_name = call.from_user.last_name or ""
    user_name = (call.from_user.first_name or "") + (" " + last_name if last_name else "")

    _, request, country = call.data.split("/")
    sender_service.send_application(user_id=user_id, user_name=user_name, user_ref=user_ref, chat_id=chat_id, country=int(country),
                     reason=request)
    if chat_id in to_edit:
        del to_edit[chat_id]
    return




@bot.callback_query_handler(func=lambda c: c.data.startswith("chc"))
def handle_change_coef(call):
    bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    _, table_name = call.data.split("/")
    admin_change_coef_states[chat_id] = table_name
    bot.send_message(chat_id,
                     text="✏️Введите новую наценку в процентах в формате десятичной дроби (1.0 = 1%; 1.5=1.5%):\n\n"
                          "<i>Число не должно быть меньше 0</i>\n", parse_mode="HTML")
    bot.register_next_step_handler(call.message, process_coef_change)
    return
@bot.callback_query_handler(func=lambda c: c.data.startswith("apq"))
def handle_application_confirm(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    user_ref = call.from_user.username
    chat_id = call.message.chat.id
    bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
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
    return





@bot.callback_query_handler(func=lambda c: c.data in ("bybit_add","comment_menu","contact_client" ))
def handle_other_callbacks(call):
    bot.answer_callback_query(call.id)
    global admin_change_coef_states, to_edit
    chat_id = call.message.chat.id
    last_name = call.from_user.last_name or ""
    user_name = (call.from_user.first_name or "") + (" " + last_name if last_name else "")
    message_id = call.message.message_id
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
        return
    if call.data == "comment_menu":
        msg = ('<b>Мы дорожим нашей репутацией, благодаря этому наш сервис работает уже 3 года.⭐️\n\n'
               '✅Про нас писали в газете <a href="https://t.me/review_2change/394">«Один из популярных сервисов обмена Турции»</a>\n'
               '✅Рекомендация сервиса <a href="https://journal.tinkoff.ru/kak-pomeniat-dengi-v-turtsii-v-2024/https://journal.tinkoff.ru/kak-pomeniat-dengi-v-turtsii-v-2024/">2Сhange в Тинькоф Журнале</a>\n'
               '✅Рекомендация на <a href="https://vc.ru/u/2800953-nikita-ryabkov/1012718-kak-obmenyat-dengi-v-turcii-vse-rabochie-sposoby-v-2024-godu?ysclid=m2men5tdyu815248852">VC.RU</a>\n'
               '✅Популярный <a href="https://t.me/brizhak_ilia/1703">тревел-блоггер Илья Брижак о нас</a>\n'
               '✅Бизнес-школа Бизнес Факт и бизнес-тренер №1 <a href="https://t.me/review_2pay/22">Алексей Максимченков рекомендуют наш сервис</a>\n'
               '✅Официальный партнер проекта <a href="https://t.me/slavianskiy_forum">«Эмигрант 360»</a>\n'
               '✅Про нас опубликовали видео <a href="https://www.youtube.com/watch?v=L1zMcBJQDjI">на популярном YouTube канале про Турцию</a>\n'
               '✅Отзывы по обмену валют - @review_2change\n'
               '✅Отзывы по оплате зарубежных сервисов и денежных переводов, открытия карт - @review_2pay\n\n</b>'
               'Смотрите больше отзывов в группе или оставьте свой')
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("Смотреть отзывы🔎", url="https://t.me/review_2change"))
        keyboard.add(InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
        bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)
        return
    if call.data == "contact_client":

        _, client_id, client_ref = qdb.get_user_name(message_id)
        if client_id or client_ref:
            new_text = call.message.text + "\n" + f"\n✅<b>Взят в работу:</b>\n<i>{datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}</i>\n\n💼Менеджер: {user_name} " + "\n" + f"\n<a href='tg://user?id={client_id}'>👉Cсылка на чат с клиентом👈</a> {f"@{client_ref}" if client_ref else ""}"
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text, parse_mode="HTML", reply_markup=None)
            logger.info(f"[ЗАЯВКА ВЗЯТА] Менеджер {user_name} взял заявку клиента {client_ref if client_ref else client_id}  в {datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")} ")
        else:
            new_text = call.message.text + "\n" + f"\n✅<b>Взят в работу:</b>\n<i>{datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}</i>\n\n💼Менеджер: {user_name} " + "\n" + f"\n<b>⚠️НЕТ ССЫЛКИ! У клиента отключен доступ к профилю по ссылке и отсутствует юзернейм. Клиенту был отправлен юзернейм менеджера⚠️</b>"
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text, parse_mode="HTML",
                                  reply_markup=None)
        return



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
            bot.register_next_step_handler(message, process_coef_change)
            return
        flmes /= 100

        qdb.set_coef(admin_change_coef_states[chat_id], flmes)
        bot.send_message(chat_id, "✅Наценка изменена! Изменения появятся в течение 5 минут.")

    except Exception as e:
        bot.send_message(chat_id, f"Что-то пошло не так, уведомили программиста:\n\n"
                                  f"{e}")




