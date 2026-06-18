
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from services.senders import SenderService


class StartHandlers:
    def __init__(self, bot, user_db, state_manager, sender_service: SenderService, deeplinks=None):
        self.bot = bot
        self.user_db = user_db
        self.send_media = sender_service.send_media
        self.clearstate = state_manager.clear
        self.deeplinks = deeplinks

    def register(self):


        def build_start(message):
            chat_id = message.chat.id
            self.clearstate(chat_id)

            keyboard = InlineKeyboardMarkup(row_width=2)
            keyboard.row(
                InlineKeyboardButton("🇹🇷 Турция", callback_data="tr_menu"),
                InlineKeyboardButton("🇹🇭 Таиланд", callback_data="thai_menu")
            )
            keyboard.row(
                InlineKeyboardButton("🇨🇳Китай", callback_data="cn_menu"),
                InlineKeyboardButton("🇰🇷Корея", callback_data="kr_menu")
            )
            keyboard.row(
                InlineKeyboardButton("🇷🇺 Россия (USDT)", callback_data="rf_menu"),
                InlineKeyboardButton("🇻🇳 Вьетнам", callback_data="vn_menu")
            )

            keyboard.add(InlineKeyboardButton("📥Пополнить Bybit Card (USDT)", callback_data="bybit_menu"))
            keyboard.add(InlineKeyboardButton("🔵Пополнить AppStore", callback_data="appstore_menu"))
            keyboard.add(InlineKeyboardButton("🛡 Гарантии и отзывы", callback_data="comment_menu"))

            keyboard.row(
                InlineKeyboardButton("📲Симкарта eSIM", callback_data="esim_main"),
                InlineKeyboardButton("💳 Зарубежная карта", callback_data="tr_card_menu")
            )

            msg = (
        "<b>💎Калькулятор 2Change — выберите услугу по кнопке ниже</b>\n\n"
        "<blockquote>🕒График работы ПН–СБ 10:00-20:00 (МСК)\n"
        "🙏<a href='https://t.me/review_2change/1014'>Отзывы (Более 11 500 отзывов за 5 лет работы)</a>\n"
        "🏦 Нам доверяют: МТС, VK, Ozon Банк, Яндекс.Плюс\n"
        "👩‍💻<a href='https://t.me/ALEXANDRA_2CHANGE'>Поддержка</a>\n"
        "⚡️<a href='https://2change.pro/'>Официальный сайт</a>\n"
        "❤️<a href='https://www.youtube.com/@2change_obmen_official'>Youtube канал</a>"
        "</blockquote>\n"
    )

            self.send_media("img/intro.jpg", chat_id, msg, parse_mode="HTML", reply_markup=keyboard)

        # 👉 /start
        @self.bot.message_handler(commands=['start'])
        @self.user_db.track_start()
        def handle_start(message):
            # deep-link на конкретное меню: payload = <menu_key>__<источник>
            parts = (message.text or "").split(maxsplit=1)
            payload = parts[1].strip() if len(parts) > 1 else None
            if self.deeplinks and self.deeplinks.logger:
                self.deeplinks.logger.info(f"/start payload={payload!r}")
            if payload and self.deeplinks and "__" in payload:
                menu_key = payload.split("__", 1)[0]
                if self.deeplinks.open(message, menu_key):
                    return
            build_start(message)

        # 👉 main_menu callback
        @self.bot.callback_query_handler(lambda c: c.data == "main_menu")
        def handle_main_menu(call):
            self.bot.answer_callback_query(call.id)
            build_start(call.message)