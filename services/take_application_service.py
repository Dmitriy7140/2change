from datetime import datetime


class ContactHandlers:
    def __init__(self, bot, qdb, logger):
        self.bot = bot
        self.qdb = qdb
        self.logger = logger

    def register(self):

        @self.bot.callback_query_handler(func=lambda c: c.data == "contact_client")
        def handle(call):
            self.handle_contact(call)

    # -------------------------
    # 📌 CONTACT CLIENT
    # -------------------------
    def handle_contact(self, call):
        self.bot.answer_callback_query(call.id)

        chat_id = call.message.chat.id
        message_id = call.message.message_id

        last_name = call.from_user.last_name or ""
        user_name = (call.from_user.first_name or "") + (" " + last_name if last_name else "")

        _, client_id, client_ref = self.qdb.get_user_name(message_id)

        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        base_text = call.message.text or ""

        # -------------------------
        # 📌 есть клиент
        # -------------------------
        if client_id or client_ref:

            new_text = (
                base_text +
                f"\n\n✅<b>Взят в работу:</b>\n"
                f"<i>{now}</i>\n\n"
                f"💼Менеджер: {user_name}\n"
                f"\n<a href='tg://user?id={client_id}'>👉Ссылка на чат с клиентом👈</a> "
                f"{f'@{client_ref}' if client_ref else ''}"
            )

            self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=new_text,
                parse_mode="HTML",
                reply_markup=None
            )

            self.logger.info(
                f"[ЗАЯВКА ВЗЯТА] {user_name} -> {client_ref or client_id} @ {now}"
            )

        # -------------------------
        # 📌 нет ссылки
        # -------------------------
        else:

            new_text = (
                base_text +
                f"\n\n✅<b>Взят в работу:</b>\n"
                f"<i>{now}</i>\n\n"
                f"💼Менеджер: {user_name}\n\n"
                f"<b>⚠️НЕТ ССЫЛКИ! У клиента отключен профиль или username отсутствует</b>"
            )

            self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=new_text,
                parse_mode="HTML",
                reply_markup=None
            )