from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Callable

from handlers.webapp import calc_button


class KoreaHandlers:
    def __init__(self, bot, subscription_service, send_media, fin_instr_class_obj, state_manager, track_user):
        self.bot = bot
        self.subscription_service = subscription_service
        self.send_media = send_media
        self.finstr = fin_instr_class_obj
        self.clearstate = state_manager.clear
        self.track = track_user

        self.routes : dict[str, Callable] = {
            "kr_menu": self.kr_menu,
            "kr_currency_menu": self.kr_currency_menu,
            "kr_cash_transactions_menu" : self.kr_cash_transactions_menu,
            "kr_edu": self.kr_edu,
        }
    def register(self):
        @self.bot.callback_query_handler(func=lambda c: c.data.startswith("kr"))
        @self.track(state="korea")

        @self.subscription_service.require_subscription(5)
        def handle_call(call):
            self.handle_korea(call)
    def handle_korea(self, call):
        self.bot.answer_callback_query(call.id)
        data = call.data

        handler = self.routes.get(data)

        if handler:
            handler(call)

    def kr_menu(self, call):

        chat_id = call.message.chat.id
        self.clearstate(chat_id)
        msg = ("<b>🇰🇷2Change - услуги в Корее</b>\n\n"
               ""
               "🕓График работы:\n"
               "Пн-Сб 10:00 - 20:00 (Вс - выходной)")

        kb = InlineKeyboardMarkup()
        kb.add(calc_button())
        kb.add(InlineKeyboardButton("📈Актуальный курс", callback_data="kr_currency_menu"))
        kb.add(InlineKeyboardButton("🎁Бесплатная симкарта eSIM", callback_data="esim_kr"))
        kb.row(InlineKeyboardButton("Наличные воны🏧", callback_data="kr_cash_transactions_menu"),
               InlineKeyboardButton("Оплата обучения📚", callback_data="kr_edu"))
        kb.add(InlineKeyboardButton("Зарубежная карта💳", callback_data="tr_card_menu"))
        kb.add(InlineKeyboardButton("Меню📋", callback_data="main_menu"))
        self.send_media('img/korea.jpg', chat_id= chat_id, caption= msg, parse_mode="HTML", reply_markup=kb)

        return
    def kr_currency_menu(self, call):
        chat_id = call.message.chat.id

        msg = self.finstr.show_currency(country=5)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(calc_button("✏️Рассчитать сумму"))
        keyboard.add(InlineKeyboardButton("👩‍💻 Позвать оператора", callback_data="request/❔вопрос про курсы валют/5"))
        self.bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)
        return
    def kr_cash_transactions_menu(self, call):
        chat_id = call.message.chat.id
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
        kb.add(calc_button())
        kb.add(InlineKeyboardButton("🎁Бесплатная симкарта eSIM", callback_data="esim_kr"))
        kb.row(InlineKeyboardButton("◀️Назад", callback_data="kr_menu"),
               InlineKeyboardButton("📋Меню", callback_data="main_menu"))
        self.send_media("img/krw_cash.MP4", chat_id=chat_id, caption=msg, reply_markup=kb, parse_mode="HTML")
        return
    def kr_edu(self, call):
        chat_id = call.message.chat.id
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
               InlineKeyboardButton("📋Меню", callback_data="main_menu"))
        self.send_media("img/kr_edu_pic.jpg", chat_id, msg, reply_markup=kb, parse_mode="HTML")
        return