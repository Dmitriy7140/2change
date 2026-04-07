from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Callable

class AppstoreHandlers:
    def __init__(self, bot, subscription_service, send_media, state_manager):
        self.bot = bot
        self.subscription_service = subscription_service
        self.send_media = send_media

        self.clearstate = state_manager.clear

        self.routes : dict[str, Callable] = {
            "appstore_menu": self.appstore_menu,
            "appstore_currency": self.appstore_currency,
        }
    def register(self):
        @self.bot.callback_query_handler(lambda c: c.data.startswith("appstore"))

        def handle_call(call):
            self.handle_appstore(call)

    def handle_appstore(self, call):
        self.bot.answer_callback_query(call.id)
        data = call.data

        handler = self.routes.get(data)

        if handler:
            handler(call)
    def appstore_menu(self, call):
        chat_id = call.message.chat.id
        self.clearstate(chat_id)

        msg = ("<b>📱 Бесплатно поможем сменить регион в App Store на Турцию и пополнить для оплат любых подписок и приложений за 5 минут!</b>\n\n"

                "<b>⭐️Как это работает?</b>\n"
                "<blockquote>1) Присылаем вам короткую инструкцию по смене региона (бесплатно, занимает 5 минут) \n"
                "2) Вы самостоятельно меняете регион на Турцию (с нашей поддержкой 24/7)\n "
                "3) Пополняете турецкий App Store лирами через СБП/Тбанк\n"
                "4) Оплачиваете подписки, приложения и игры как и раньше в 2-5 раз дешевле!</blockquote>\n\n"
                "<b>Услуга бесплатная!</b>")
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✏️Сделать расчет", style="success", callback_data="appstore_currency"))

        keyboard.add(InlineKeyboardButton("Меню📋", callback_data="main_menu"))
        self.send_media("img/appstore.jpg",chat_id, msg, parse_mode="HTML", reply_markup=keyboard)

        return
    def appstore_currency(self, call):
        chat_id = call.message.chat.id
        self.clearstate(chat_id)

        msg = ("<b>Актуальный курс пополнения Appstore</b>\n\n"
            "<b>🇹🇷500 лир = 2500 руб\n"
            "🇹🇷1000 лир = 4900 руб \n"
            "🇹🇷5000 лир = 23500 руб \n"
            "💰Другая сумма по запросу\n</b>")
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🇹🇷+500 лир", callback_data="request/📱 Appstore +500 лир/1"))
        keyboard.add(InlineKeyboardButton("🇹🇷+1000 лир", callback_data="request/📱 Appstore +1000 лир/1"))
        keyboard.add(InlineKeyboardButton("🇹🇷+5000 лир", callback_data="request/📱 Appstore +5000 лир/1"))
        keyboard.add(InlineKeyboardButton("💰Другая сумма", callback_data="request/📱 Appstore пополнение/1"))
        keyboard.add(InlineKeyboardButton("Меню📋", callback_data="main_menu"))
        self.bot.send_message( chat_id, msg, parse_mode="HTML", reply_markup=keyboard)

        return
