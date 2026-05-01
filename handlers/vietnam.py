from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Callable



class VietnamHandlers:
    def __init__(self, bot, subscription_service, send_media, fin_instr_class_obj, state_manager, track_user):
        self.bot = bot
        self.subscription_service = subscription_service
        self.send_media = send_media
        self.finstr = fin_instr_class_obj
        self.clearstate = state_manager.clear
        self.track = track_user

        self.routes : dict[str, Callable] = {
            "vn_menu": self.vn_menu,
            "vn_currency_menu": self.vn_currency_menu,

        }
    def register(self):
        @self.bot.callback_query_handler(func=lambda c: c.data.startswith("vn"))
        @self.track(state="vietnam")

        @self.subscription_service.require_subscription(7)
        def handle_call(call):
            self.handle_vietnam(call)
    def handle_vietnam(self, call):
        self.bot.answer_callback_query(call.id)
        data = call.data

        handler = self.routes.get(data)

        if handler:
            handler(call)

    def vn_menu(self, call):

        chat_id = call.message.chat.id
        self.clearstate(chat_id)
        msg = ("<b>🇻🇳2Change - услуги во Вьетнаме</b>\n\n"
               ""
               "🕓График работы:\n"
               "Пн-Сб 10:00 - 20:00 (Вс - выходной)")

        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("✏️Сделать расчет", style="success",callback_data="calc_vn"))
        kb.add(InlineKeyboardButton("📈Актуальный курс", callback_data="vn_currency_menu"))
        kb.add(InlineKeyboardButton("Зарубежная карта💳", callback_data="tr_card_menu"))
        kb.add(InlineKeyboardButton("Меню📋", callback_data="main_menu"))
        self.bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=kb)

        return
    def vn_currency_menu(self, call):
        chat_id = call.message.chat.id

        msg = self.finstr.show_currency(country=7)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✏️Сделать расчет", style="success",callback_data="calc_vn"))

        keyboard.add(InlineKeyboardButton("👩‍💻 Позвать оператора", callback_data="request/❔вопрос про курсы валют/7"))
        keyboard.add(InlineKeyboardButton("Меню📋", callback_data="main_menu"))
        self.bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)
        return
