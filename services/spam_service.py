from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
from config import ADMIN_IDS


class SpamService:
    def __init__(self, bot, user_db, state_manager, logger):
        self.bot = bot
        self.user_db = user_db
        self.state = state_manager
        self.logger = logger

    # -------------------------
    # 📌 REGISTER
    # -------------------------
    def register(self):

        @self.bot.message_handler(commands=['announce'])
        def start(message):
            if message.from_user.id not in ADMIN_IDS:
                return

            self.start_announce(message)

        @self.bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'animation'])
        def catch_message(message):
            self.catch_payload(message)

        @self.bot.callback_query_handler(func=lambda c: c.data.startswith("announce_"))
        def handle_group(call):
            self.handle_group(call)

        @self.bot.callback_query_handler(func=lambda c: c.data.startswith("confirm_announce"))
        def handle_confirm(call):
            self.handle_confirm(call)

        @self.bot.callback_query_handler(func=lambda c: c.data == "cancel_announce")
        def cancel(call):
            self.cancel(call)

    # -------------------------
    # 📌 KEYBOARDS
    # -------------------------
    def _group_keyboard(self):
        kb = InlineKeyboardMarkup()

        kb.row(
            InlineKeyboardButton("🇹🇷 Турция", callback_data="announce_tr"),
            InlineKeyboardButton("🇻🇳 Вьетнам", callback_data="announce_vn"),
        )
        kb.row(
            InlineKeyboardButton("🇰🇷 Корея", callback_data="announce_kr"),
            InlineKeyboardButton("🇷🇺 Россия", callback_data="announce_ru"),
        )
        kb.row(
            InlineKeyboardButton("🇨🇳 Китай", callback_data="announce_cn"),
        )
        kb.add(InlineKeyboardButton("🌍 Всем", callback_data="announce_all"))
        kb.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel_announce"))

        return kb

    def _cancel_keyboard(self):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel_announce"))
        return kb

    def _confirm_keyboard(self, group):
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton(
                "🚀 Отправить",
                callback_data=f"confirm_announce/{group}"
            )
        )
        kb.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel_announce"))
        return kb

    # -------------------------
    # 📌 STEP 1: start
    # -------------------------
    def start_announce(self, message):
        chat_id = message.chat.id

        self.state.set(chat_id, {
            "mode": "announce_wait_group"
        })

        self.bot.send_message(
            chat_id,
            "📢 Выбери, кому отправить сообщение:",
            reply_markup=self._group_keyboard()
        )

    # -------------------------
    # 📌 STEP 2: group select
    # -------------------------
    def handle_group(self, call):
        self.bot.answer_callback_query(call.id)

        chat_id = call.message.chat.id
        data = call.data

        state = self.state.get(chat_id)
        if not state or state.get("mode") != "announce_wait_group":
            return

        self.state.set(chat_id, {
            "mode": "announce_wait_message",
            "group": data
        })

        self.bot.send_message(
            chat_id,
            "✏️ Отправь сообщение для рассылки",
            reply_markup=self._cancel_keyboard()
        )

    # -------------------------
    # 📌 STEP 3: capture message
    # -------------------------
    def catch_payload(self, message):
        chat_id = message.chat.id

        state = self.state.get(chat_id)
        if not state or state.get("mode") != "announce_wait_message":
            return

        self.state.set(chat_id, {
            "mode": "announce_ready",
            "group": state["group"],
            "from_chat": chat_id,
            "message_id": message.message_id
        })

        group_map = {
            "announce_tr": "Турция",
            "announce_vn": "Вьетнам",
            "announce_kr": "Корея",
            "announce_ru": "Россия",
            "announce_cn": "Китай",
            "announce_all": "ВСЕ"
        }

        group_text = group_map.get(state["group"], "выбранной группе")

        preview = self.bot.copy_message(
            chat_id=chat_id,
            from_chat_id=chat_id,
            message_id=message.message_id
        )

        self.bot.send_message(
            chat_id,
            f"📤 Отправить это сообщение пользователям ({group_text})?",
            reply_to_message_id=preview.message_id,
            reply_markup=self._confirm_keyboard(state["group"])
        )

    # -------------------------
    # 📌 STEP 4: send
    # -------------------------
    def handle_confirm(self, call):
        self.bot.answer_callback_query(call.id)

        chat_id = call.message.chat.id
        payload = self.state.get(chat_id)

        if not payload:
            self.bot.send_message(chat_id, "Сессия истекла")
            return

        group = payload.get("group")

        group_map = {
            "announce_tr": "turkey",
            "announce_vn": "vietnam",
            "announce_kr": "korea",
            "announce_ru": "russia",
            "announce_cn": "china",
        }

        # -------------------------
        # 📌 USERS FETCH
        # -------------------------
        if group == "announce_all":
            users = self.user_db.get_users()
            db_state = "ALL"
        else:
            db_state = group_map.get(group)

            if not db_state:
                self.state.clear(chat_id)
                self.bot.send_message(chat_id, "❌ Неизвестная группа")
                return

            users = self.user_db.get_users_by_state(db_state)

        # -------------------------
        # 📌 DEBUG LOG
        # -------------------------


        # -------------------------
        # 📌 SAFETY CHECK
        # -------------------------
        if not users:
            self.state.clear(chat_id)
            self.bot.send_message(chat_id, "⚠️ Нет пользователей в этой группе")
            return

        # -------------------------
        # 📌 SEND
        # -------------------------
        sent = 0
        failed = 0

        for u in users:
            try:
                self.bot.copy_message(
                    chat_id=u["telegram_id"],
                    from_chat_id=payload["from_chat"],
                    message_id=payload["message_id"]
                )
                sent += 1
                time.sleep(0.03)

            except Exception as e:
                failed += 1
                self.logger.error(f"announce error {u['telegram_id']}: {e}")

        self.state.clear(chat_id)

        self.bot.send_message(
            chat_id,
            f"📢 Рассылка завершена\n"
            f"✅ Успешно: {sent}\n"
            f"❌ Ошибок: {failed}"
        )
        self.logger.info(f"{call.from_user.id} разослал сообщения пользователям")
    # -------------------------
    # 📌 CANCEL
    # -------------------------
    def cancel(self, call):
        chat_id = call.message.chat.id

        self.state.clear(chat_id)

        self.bot.answer_callback_query(call.id, "Отменено")
        self.bot.send_message(chat_id, "❌ Рассылка отменена")