from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

class ManagerHandlers:
    def __init__(self, bot, qdb, state_manager, day_off, manager_chat_id, application_creator, track_user):
        self.bot = bot
        self.qdb = qdb
        self.state_manager = state_manager
        self.day_off = day_off
        self.manager_chat_id = manager_chat_id
        self.ApplicationCreator = application_creator
        self.track=track_user

    def register(self):

        @self.bot.message_handler(commands=['manager'])
        @self.track()

        def handle_manager(message):
            self.state_manager.clear(message.chat.id)

            last_name = message.from_user.last_name or ""
            user_name = (message.from_user.first_name or "") + (" " + last_name if last_name else "")
            user_id = message.from_user.id
            user_ref = message.from_user.username

            # 💤 нерабочее время
            if self.day_off():
                self.qdb.add_to_queue(
                    tg_id=user_id,
                    name=user_name,
                    reason="🔔вызов менеджера"
                )

                msg = (
                    "⚡️Ваша заявка уже в работе, скоро менеджер Александра с вами свяжется, "
                    "ожидайте или напишите нам @alexandra_2change\n\n"
                    "<b>🕰Наш график работы:</b>\n"
                    "ПН-СБ: 10:00 - 20:00 (ВС выходной)"
                )

                self.bot.send_message(message.chat.id, msg, parse_mode="HTML")
                return

            # 🧠 нормальный сценарий
            apmake = self.ApplicationCreator(
                client_name=user_name,
                reason="🔔вызов менеджера"
            )

            msg = apmake.create()

            keyboard = InlineKeyboardMarkup()
            keyboard.add(
                InlineKeyboardButton(
                    "💬Связаться с клиентом",
                    callback_data="contact_client"
                )
            )

            sent_msg = self.bot.send_message(
                self.manager_chat_id,
                msg,
                parse_mode="HTML",
                reply_markup=keyboard
            )

            # 📌 связываем менеджера с заявкой
            if self.qdb.set_user_name(sent_msg.message_id, user_id, user_ref):
                msg = (
                    "⚡️Ваша заявка уже в работе, скоро менеджер Александра с вами свяжется, "
                    "ожидайте или напишите нам @alexandra_2change\n\n"
                    "<b>🕰Наш график работы:</b>\n"
                    "ПН-СБ: 10:00 - 20:00 (ВС выходной)"
                )

                self.bot.send_message(message.chat.id, msg, parse_mode="HTML")
            else:
                self.bot.send_message(
                    message.chat.id,
                    "⛔️Менеджер не сможет вам написать из-за настроек приватности⛔️\n"
                    "Включите видимость профиля или напишите @ALEXANDRA_2CHANGE",
                    parse_mode="HTML"
                )