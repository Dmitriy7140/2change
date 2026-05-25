
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Callable


class ThailandHandlers:
    def __init__(self, bot, subscription_service, send_media, fin_instr_class_obj, state_manager, track_user):
        self.bot = bot
        self.subscription_service = subscription_service
        self.track= track_user
        self.send_media = send_media
        self.finstr = fin_instr_class_obj
        self.clearstate = state_manager.clear

        self.routes: dict[str, Callable] = {
            "thai_menu":self.thai_menu,
            "thai_currencies":self.thai_currencies,
        }

    def register(self):
        @self.bot.callback_query_handler(func=lambda c: c.data.startswith("thai"))
        @self.track(state="thailand")

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
        self.clearstate(chat_id)


        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✏️Сделать расчет",style="success", callback_data="calc_thai"))
        keyboard.add(InlineKeyboardButton("📈Курс", callback_data="thai_currencies"))
        keyboard.add(InlineKeyboardButton("💳Зарубежная карта", callback_data="tr_card_menu"))
        keyboard.add(InlineKeyboardButton("👩‍💻 Позвать оператора", callback_data="request/❔вопрос про курсы валют/3"))
        keyboard.add(InlineKeyboardButton("Меню📋", callback_data="main_menu"))
        self.send_media(path="img/thailand.jpg", chat_id=chat_id, caption='''🇹🇭<b>2Change — услуги в Таиланде\n\n🕒 График работы:</b>\nПн-Сб: 10:00 - 20:00 (Вс - выходной)\nОфис по записи'''
                        , parse_mode="HTML", reply_markup=keyboard)
    def thai_currencies(self, call):
        chat_id = call.message.chat.id
        self.clearstate(chat_id)

        msg = self.finstr.show_currency(country=3)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✏️Сделать расчет", style="success", callback_data="calc_thai"))
        keyboard.add(InlineKeyboardButton("💳Зарубежная карта", callback_data="tr_card_menu"))
        keyboard.add(InlineKeyboardButton("👩‍💻 Позвать оператора", callback_data="request/❔вопрос про курсы валют/3"))
        keyboard.add(InlineKeyboardButton("Меню📋", callback_data="main_menu"))
        self.bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML", reply_markup=keyboard)


        return