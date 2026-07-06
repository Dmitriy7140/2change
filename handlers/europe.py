from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Callable

from handlers.webapp import calc_button


class EuropeHandlers:
    def __init__(self, bot, fin_instr_class_obj, state_manager, track_user):
        self.bot = bot
        self.finstr = fin_instr_class_obj
        self.clearstate = state_manager.clear
        self.track = track_user

        self.routes: dict[str, Callable] = {
            "eu_menu": self.eu_menu,
            "eu_currency_menu": self.eu_currency_menu,
        }

    def register(self):
        @self.bot.callback_query_handler(func=lambda c: c.data.startswith("eu"))
        @self.track(state="europe")
        def handle_call(call):
            self.handle_europe(call)

    def handle_europe(self, call):
        self.bot.answer_callback_query(call.id)
        handler = self.routes.get(call.data)
        if handler:
            handler(call)

    def eu_menu(self, call):
        chat_id = call.message.chat.id
        self.clearstate(chat_id)

        msg = self.finstr.show_currency(country=8)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(calc_button())
        keyboard.add(InlineKeyboardButton("👩‍💻 Позвать оператора", callback_data="request/❔вопрос про евро/8"))
        keyboard.add(InlineKeyboardButton("Меню📋", callback_data="main_menu"))
        self.bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)

    def eu_currency_menu(self, call):
        chat_id = call.message.chat.id

        msg = self.finstr.show_currency(country=8)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(calc_button())
        keyboard.add(InlineKeyboardButton("👩‍💻 Позвать оператора", callback_data="request/❔вопрос про евро/8"))
        keyboard.add(InlineKeyboardButton("◀️Назад", callback_data="eu_menu"))
        self.bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)
