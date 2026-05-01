from typing import Callable, Any

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class InfoHandlers:
    def __init__(self, bot, track_user):
        self.bot = bot
        self.track = track_user
        self.routes: dict[str, Callable[[Any], None]] = {
            "comment_menu": self.comment_menu,
        }
    def register(self):

        @self.bot.callback_query_handler(
            func=lambda c: c.data in self.routes
        )
        @self.track()

        def handle(call):
            self.bot.answer_callback_query(call.id)

            handler = self.routes.get(call.data)
            if handler:
                handler(call)

    # -------------------------
    # 📌 COMMENT MENU
    # -------------------------
    def comment_menu(self, call):
        chat_id = call.message.chat.id

        msg = ('<b>Мы дорожим нашей репутацией, благодаря этому наш сервис работает уже 3 года.⭐️\n\n'
               '✅Про нас писали в газете <a href="https://t.me/review_2change/394">«Один из популярных сервисов обмена Турции»</a>\n'
               '✅Рекомендация сервиса <a href="https://journal.tinkoff.ru/kak-pomeniat-dengi-v-turtsii-v-2024/https://journal.tinkoff.ru/kak-pomeniat-dengi-v-turtsii-v-2024/">2Сhange в Тинькоф Журнале</a>\n'
               '✅Рекомендация на <a href="https://vc.ru/u/2800953-nikita-ryabkov/1012718-kak-obmenyat-dengi-v-turcii-vse-rabochie-sposoby-v-2024-godu?ysclid=m2men5tdyu815248852">VC.RU</a>\n'
               '✅Популярный <a href="https://t.me/brizhak_ilia/1703">тревел-блоггер Илья Брижак о нас</a>\n'
               '✅Бизнес-школа Бизнес Факт и бизнес-тренер №1 <a href="https://t.me/review_2pay/22">Алексей Максимченков рекомендуют наш сервис</a>\n'
               '✅Официальный партнер проекта <a href="https://t.me/slavianskiy_forum">«Эмигрант 360»</a>\n'
               '✅Про нас опубликовали видео <a href="https://www.youtube.com/watch?v=L1zMcBJQDjI">на популярном YouTube канале про Турцию</a>\n'
               '✅Отзывы по обмену валют - @review_2change\n'
               '✅Отзывы по оплате зарубежных сервисов и денежных переводов, открытия карт - @review_2pay\n\n</b>'
               'Смотрите больше отзывов в группе или оставьте свой')

        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton(
                "Смотреть отзывы🔎",
                url="https://t.me/review_2change"
            )
        )
        keyboard.add(
            InlineKeyboardButton(
                "Меню📋",
                callback_data="main_menu"
            )
        )

        self.bot.send_message(
            chat_id,
            msg,
            parse_mode="HTML",
            reply_markup=keyboard
        )