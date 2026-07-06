from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Callable

from handlers.webapp import calc_button




class ChinaHandlers:
    def __init__(self, bot, subscription_service, send_media, fin_instr_class_obj, state_manager, track_user):

        self.bot = bot
        self.subscription_service = subscription_service
        self.send_media = send_media
        self.finstr = fin_instr_class_obj
        self.clearstate = state_manager.clear
        self.track = track_user

        self.routes : dict[str, Callable] = {
            "cn_menu":self.cn_menu,
            "cn_alipay":self.cn_alipay,
            "cn_faq":self.cn_faq,
            "cn_currency_menu":self.cn_currency_menu
        }
    def register(self):
        @self.bot.callback_query_handler(func=lambda c: c.data.startswith("cn"))
        @self.track(state="china")
        @self.subscription_service.require_subscription(4)
        def handle_call(call):
            self.handle_china(call)
    def handle_china(self, call):
        self.bot.answer_callback_query(call.id)
        data = call.data

        handler = self.routes.get(data)

        if handler:
            handler(call)
    def cn_menu(self, call):
        chat_id = call.message.chat.id
        self.clearstate(chat_id)
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
        kb.add(calc_button())
        kb.add(InlineKeyboardButton("📈Актуальный курс", callback_data="cn_currency_menu"))
        kb.add(InlineKeyboardButton("📲Cимкарта eSIM", callback_data="esim_cn"))
        kb.add(InlineKeyboardButton("💳Регистрация Alipay", callback_data="cn_alipay"))
        kb.add(InlineKeyboardButton("❓Как пополнить Alipay/Wechat", callback_data="cn_faq"))
        kb.add(InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
        self.send_media("img/china.jpg", chat_id=chat_id, caption=msg, parse_mode="HTML",
                                  reply_markup=kb)

        return
    def cn_alipay(self, call):
        chat_id = call.message.chat.id

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
        kb.row(InlineKeyboardButton("◀️Назад", callback_data="cn_menu"),
               InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))

        self.send_media("img/cn_alipay.jpg", chat_id=chat_id, caption=msg, parse_mode="HTML", reply_markup=kb)

        return
    def cn_faq(self, call):

        chat_id = call.message.chat.id
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
        self.send_media("img/cn_ap_wc.jpg", chat_id=chat_id, caption=msg, parse_mode="HTML", reply_markup=kb)

        return
    def cn_currency_menu(self, call):
        chat_id = call.message.chat.id

        msg = self.finstr.show_currency(country=4)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(calc_button())
        keyboard.add(InlineKeyboardButton("💳Зарубежная карта", callback_data="tr_card_menu"))
        keyboard.add(InlineKeyboardButton("👩‍💻 Позвать оператора", callback_data="request/❔вопрос про курсы валют/4"))
        self.bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)
        return