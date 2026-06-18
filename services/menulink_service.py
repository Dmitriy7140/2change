"""
/menulink — генератор deep-link'ов для админа (только ADMIN_IDS).

Шаг 1: выбрать пункт меню (панель с пагинацией).
Шаг 2: ввести источник трафика (например tgads).

Итог: payload = "<callback_data>__<источник>", напр. tr_card_menu__tgads,
и готовая ссылка t.me/<bot>?start=<payload>.
Разбор payload — в handlers/start.py: до "__" — меню (callback_data),
после "__" — источник, который пишется в аналитику.
"""
import re

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import ADMIN_IDS


class MenuLinkService:

    SEPARATOR = "__"
    MAX_PAYLOAD = 64           # лимит Telegram на start-параметр
    PAGE_SIZE = 5              # кнопок назначения на странице

    # подпись -> callback_data (порядок = порядок в панели)
    DESTINATIONS = [
        ("🇹🇷 Меню Турции", "tr_menu"),
        ("🇰🇷 Меню Кореи", "kr_menu"),
        ("🇨🇳 Меню Китая", "cn_menu"),
        ("🇻🇳 Меню Вьетнама", "vn_menu"),
        ("🇷🇺 Меню России", "rf_menu"),
        ("🇹🇭 Меню Таиланда", "thai_menu"),
        ("💳 Зарубежная карта", "tr_card_menu"),
        ("📲 eSIM (главное меню)", "esim_main"),
        ("📥 Bybit", "bybit_menu"),
        ("📈 Курс Турции", "tr_currency_menu"),
        ("📈 Курс Китая", "cn_currency_menu"),
        ("📈 Курс Кореи", "kr_currency_menu"),
        ("📈 Курс Таиланда", "thai_currencies"),
        ("📈 Курс Вьетнама", "vn_currency_menu"),
    ]

    _NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self._username = None
        self._labels = {cb: label for label, cb in self.DESTINATIONS}

    # -------------------------
    # 📌 REGISTER
    # -------------------------
    def register(self):

        @self.bot.message_handler(commands=['menulink'])
        def start(message):
            if message.from_user.id not in ADMIN_IDS:
                return
            self.start_menulink(message)

        @self.bot.callback_query_handler(func=lambda c: c.data == "mlink_noop")
        def noop(call):
            self.bot.answer_callback_query(call.id)

        @self.bot.callback_query_handler(func=lambda c: c.data.startswith("mlink_page/"))
        def page(call):
            self.handle_page(call)

        @self.bot.callback_query_handler(func=lambda c: c.data.startswith("mlink_pick/"))
        def pick(call):
            self.handle_pick(call)

        @self.bot.callback_query_handler(func=lambda c: c.data == "mlink_cancel")
        def cancel(call):
            self.handle_cancel(call)

    # -------------------------
    # 📌 HELPERS
    # -------------------------
    def _bot_username(self):
        if not self._username:
            self._username = self.bot.get_me().username
        return self._username

    def _pages_count(self):
        total = len(self.DESTINATIONS)
        return (total + self.PAGE_SIZE - 1) // self.PAGE_SIZE

    def _page_keyboard(self, page):
        pages = self._pages_count()
        page = max(0, min(page, pages - 1))

        start = page * self.PAGE_SIZE
        chunk = self.DESTINATIONS[start:start + self.PAGE_SIZE]

        kb = InlineKeyboardMarkup()
        for label, cb in chunk:
            kb.add(InlineKeyboardButton(label, callback_data=f"mlink_pick/{cb}"))

        # пагинация всегда в виде: ◀️  N/M  ▶️ (на краях стрелка неактивна)
        left = f"mlink_page/{page - 1}" if page > 0 else "mlink_noop"
        right = f"mlink_page/{page + 1}" if page < pages - 1 else "mlink_noop"
        kb.row(
            InlineKeyboardButton("◀️", callback_data=left),
            InlineKeyboardButton(f"{page + 1}/{pages}", callback_data="mlink_noop"),
            InlineKeyboardButton("▶️", callback_data=right),
        )

        kb.add(InlineKeyboardButton("❌ Отмена", callback_data="mlink_cancel"))
        return kb

    # -------------------------
    # 📌 STEP 1: /menulink
    # -------------------------
    def start_menulink(self, message):
        self.bot.send_message(
            message.chat.id,
            "🔗 <b>Генератор ссылок</b>\n\nВыбери, куда поведёт ссылка:",
            reply_markup=self._page_keyboard(0),
            parse_mode="HTML"
        )

    # -------------------------
    # 📌 ПАГИНАЦИЯ
    # -------------------------
    def handle_page(self, call):
        self.bot.answer_callback_query(call.id)
        if call.from_user.id not in ADMIN_IDS:
            return
        try:
            page = int(call.data.split("/", 1)[1])
        except ValueError:
            return
        self.bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=self._page_keyboard(page)
        )

    # -------------------------
    # 📌 STEP 2: выбор назначения
    # -------------------------
    def handle_pick(self, call):
        self.bot.answer_callback_query(call.id)
        if call.from_user.id not in ADMIN_IDS:
            return

        chat_id = call.message.chat.id
        callback_data = call.data.split("/", 1)[1]

        if callback_data not in self._labels:
            self.bot.send_message(chat_id, "❌ Неизвестный пункт")
            return

        self.bot.send_message(
            chat_id,
            f"Пункт: <code>{callback_data}</code>\n\n"
            f"✏️ Теперь введи <b>источник</b> (метку канала/рекламы), например <code>tgads</code>.\n"
            f"<i>Латиница, цифры, _ и - — без пробелов.</i>",
            parse_mode="HTML"
        )

        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.bot.register_next_step_handler_by_chat_id(
            chat_id,
            self.make_link,
            callback_data
        )

    # -------------------------
    # 📌 STEP 3: ввод источника -> ссылка
    # -------------------------
    def make_link(self, message, callback_data):
        if message.from_user.id not in ADMIN_IDS:
            return

        chat_id = message.chat.id
        source = (message.text or "").strip()

        if not self._NAME_RE.match(source):
            self.bot.send_message(
                chat_id,
                "⚠️ Только латиница, цифры, _ и - (без пробелов).\n"
                "Запусти /menulink заново."
            )
            return

        if self.SEPARATOR in source:
            self.bot.send_message(
                chat_id,
                f"⚠️ Источник не должен содержать «{self.SEPARATOR}».\n"
                "Запусти /menulink заново."
            )
            return

        payload = f"{callback_data}{self.SEPARATOR}{source}"
        if len(payload) > self.MAX_PAYLOAD:
            self.bot.send_message(
                chat_id,
                f"⚠️ Слишком длинно (payload {len(payload)} > {self.MAX_PAYLOAD}). Сократи источник."
            )
            return

        url = f"https://t.me/{self._bot_username()}?start={payload}"

        self.bot.send_message(
            chat_id,
            f"✅ Готово — ссылка на «{self._labels[callback_data]}»:\n\n"
            f"<code>{url}</code>\n\n"
            f"📌 Источник в аналитике: <code>{source}</code>",
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        self.logger.info(f"{message.from_user.id} сгенерировал menulink: {payload}")

    # -------------------------
    # 📌 CANCEL
    # -------------------------
    def handle_cancel(self, call):
        self.bot.answer_callback_query(call.id, "Отменено")
        chat_id = call.message.chat.id
        self.bot.clear_step_handler_by_chat_id(chat_id)
        try:
            self.bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=None
            )
        except Exception:
            pass
