from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
class ApplicationConfirmService:
    def __init__(self, bot, qdb, manager_chat_id, application_creator):
        self.bot = bot
        self.qdb = qdb
        self.manager_chat_id = manager_chat_id
        self.ApplicationCreator = application_creator

    def register(self):

        @self.bot.callback_query_handler(func=lambda c: c.data.startswith("apq"))
        def handle(call):
            self.handle_apq(call)

    def handle_apq(self, call):
        self.bot.answer_callback_query(call.id)

        chat_id = call.message.chat.id
        user_id = call.from_user.id
        user_ref = call.from_user.username

        self.bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)

        _, verdict, tg_id = call.data.split("/")

        _, tg_id, country, client_name, amount1, amount2, currency1, currency2, reason, created_at = \
            self.qdb.get_from_queue(get_by_id=tg_id)

        if verdict == "y":

            keyboard = InlineKeyboardMarkup()
            keyboard.add(
                InlineKeyboardButton(
                    "💬Связаться с клиентом",
                    callback_data="contact_client",
                    style="success"
                )
            )

            apmake = self.ApplicationCreator(
                country=country,
                client_name=client_name,
                reason=reason,
                currency1=currency1,
                currency2=currency2,
                amount1=amount1,
                amount2=amount2,
                time=created_at
            )

            msg = apmake.create()

            sent_msg = self.bot.send_message(
                self.manager_chat_id,
                msg,
                parse_mode="HTML",
                reply_markup=keyboard
            )

            if self.qdb.set_user_name(sent_msg.message_id, user_id, user_ref):
                self.bot.send_message(
                    tg_id,
                    "✅Заявка подтверждена, менеджер ответит вам в ближайшее время!"
                )
            else:
                self.bot.send_message(
                    chat_id,
                    "⛔️Менеджер не сможет вам написать (приватность)",
                    parse_mode="HTML"
                )

        else:
            self.bot.send_message(tg_id, "❌Заявка отменена")