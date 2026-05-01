from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time

class QueueHandler:
    def __init__(self, bot, qdb, manager_chat_id):
        self.bot = bot
        self.qdb = qdb
        self.manager_chat_id = manager_chat_id

    def run(self):
        lines = self.qdb.get_from_queue(True)

        if not lines:
            self.bot.send_message(self.manager_chat_id, "Заявок в очереди нет.")
            return

        for i in lines:
            _, tg_id, country, client_name, amount1, amount2, currency1, currency2, reason, created_at = i

            keyboard = InlineKeyboardMarkup()
            keyboard.row(
                InlineKeyboardButton("✅", style="success", callback_data=f"apq/y/{tg_id}"),
                InlineKeyboardButton("❌", style="danger", callback_data=f"apq/n/{tg_id}")
            )

            text = (
                f"Здравствуйте, {client_name}!\n\n"
                f"Подскажите, актуальна ли заявка?\n\n"
                f"{reason if reason else f'<b>Обмен:</b> {currency1} → {currency2}\n\nСумма: {amount1} {currency1}'}"
            )

            self.bot.send_message(
                tg_id,
                text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )

            time.sleep(0.03)