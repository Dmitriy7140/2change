from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Callable

class BybitHandlers:
    def __init__(self, bot, subscription_service, send_media, fin_instr_class_obj, state_manager):
        self.bot = bot
        self.subscription_service = subscription_service
        self.send_media = send_media
        self.finstr = fin_instr_class_obj
        self.clearstate = state_manager.clear

        self.routes : dict[str, Callable] = {
            "bybit_menu": self.bybit_menu,
        }
    def register(self):
        @self.bot.callback_query_handler(lambda c: c.data.startswith("bybit"))

        def handle_call(call):
            self.handle_bybit(call)

    def handle_bybit(self, call):
        self.bot.answer_callback_query(call.id)
        data = call.data

        handler = self.routes.get(data)

        if handler:
            handler(call)
    def bybit_menu(self, call):
        chat_id = call.message.chat.id
        self.clearstate(chat_id)

        msg = self.finstr.show_currency(country=100)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✏️Сделать расчет",style="success", callback_data="exchange/rub/usd/100"))
        keyboard.add(InlineKeyboardButton("👩‍💻 Позвать оператора", callback_data="request/❔Что такое Bybit/100"))
        keyboard.add(InlineKeyboardButton("Меню📋", callback_data="main_menu"))
        self.bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)

        return