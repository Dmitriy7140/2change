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
from services.interest_service import InterestService

from handlers.turkey import TurkeyHandlers
from handlers.korea import KoreaHandlers
from handlers.esim import EsimHandlers
from handlers.china import ChinaHandlers
from handlers.russia import RussiaHandlers
from handlers.thailand import ThailandHandlers
from handlers.vietnam import VietnamHandlers
from handlers.bybit import BybitHandlers

from sheets.interest import Interest


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
sheets_interest = Interest(logger)

bot = telebot.TeleBot(BOT_TOKEN if not TEST_MODE else TEST_BOT_TOKEN, exception_handler=MyExceptionHandler())
finstr = FinInstr()

subscription_service = SubscriptionService(bot, logger, TEST_MODE)


sender_service = SenderService(bot, qdb, manager_chat_id, day_off)

state_manager = StateManager(logger)
exchange_service = ExchangeService(bot, logger, sender_service, FinInstr, state_manager)
exchange_service.register_handlers()

interest_service = InterestService(
    bot,
    logger,

    sheets_interest,
    qdb,

    ADMIN_IDS,

)
interest_service.register()


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
bybit_handlers = BybitHandlers(
    bot,
    subscription_service,
    sender_service.send_media,
    finstr,
    state_manager,
)
bybit_handlers.register()


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
    keyboard.add(InlineKeyboardButton("🇻🇳 Вьетнам", callback_data="vn_currency_menu"))
    keyboard.add(InlineKeyboardButton("📥Пополнить Bybit Card (🪙USDT)", callback_data="bybit_menu"))
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





@bot.callback_query_handler(func=lambda c: c.data in ("comment_menu","contact_client" ))
def handle_other_callbacks(call):
    bot.answer_callback_query(call.id)
    global admin_change_coef_states, to_edit
    chat_id = call.message.chat.id
    last_name = call.from_user.last_name or ""
    user_name = (call.from_user.first_name or "") + (" " + last_name if last_name else "")
    message_id = call.message.message_id
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



