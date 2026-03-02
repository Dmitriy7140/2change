
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Callable


class ThailandHandlers:
    def __init__(self, bot, subscription_service, send_media, fin_instr_class_obj):
        self.bot = bot
        self.subscription_service = subscription_service
        self.send_media = send_media
        self.finstr = fin_instr_class_obj

        self.routes: dict[str, Callable] = {
            "thai_menu":self.thai_menu,
        }

    def register(self):
        @self.bot.callback_query_handler(func=lambda c: c.data.startswith("thai"))
        @self.subscription_service.require_subscription(3)
        def handle_call(call):
            self.handle_thai(call)

    def handle_thai(self, call):
        self.bot.answer_callback_query(call.id)
        data = call.data

        handler = self.routes.get(data)

        if handler:
            handler(call)

    def thai_menu(self, call):
        chat_id = call.message.chat.id

        msg = self.finstr.show_currency(country=3)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✏️Рассчитать сумму", callback_data="calc_thai"))
        keyboard.add(InlineKeyboardButton("💳Зарубежная карта", callback_data="tr_card_menu"))
        keyboard.add(InlineKeyboardButton("❔Задать вопрос", callback_data="request/❔вопрос про курсы валют/3"))
        keyboard.add(InlineKeyboardButton("Главное меню📋", callback_data="main_menu"))
        self.bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)

        return