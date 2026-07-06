from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Callable

from handlers.webapp import calc_button




class RussiaHandlers:
    def __init__(self, bot, subscription_service, send_media, fin_instr_class_obj, state_manager, track_user):
        self.bot = bot
        self.subscription_service = subscription_service
        self.send_media = send_media
        self.finstr = fin_instr_class_obj
        self.clearstate = state_manager.clear
        self.track = track_user


        self.routes : dict[str, Callable] = {
            "rf_menu": self.rf_menu,
        }
    def register(self):
        @self.bot.callback_query_handler(lambda c: c.data.startswith("rf"))
        @self.track(state="russia")


        def handle_call(call):
            self.handle_russia(call)

    def handle_russia(self, call):
        self.bot.answer_callback_query(call.id)
        data = call.data

        handler = self.routes.get(data)

        if handler:
            handler(call)
    def rf_menu(self, call):
        chat_id = call.message.chat.id
        self.clearstate(chat_id)

        msg = self.finstr.show_currency(country=2)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(calc_button())
        keyboard.add(InlineKeyboardButton("👩‍💻 Позвать оператора", callback_data="request/❔вопрос про курсы валют/2"))
        keyboard.add(InlineKeyboardButton("Меню📋", callback_data="main_menu"))
        self.bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)

        return