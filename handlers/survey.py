import html
from datetime import datetime, timezone, timedelta

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

MSK = timezone(timedelta(hours=3))

# номер -> (текст вопроса, [(буква, вариант ответа), ...])
QUESTIONS = {
    1: ("Вопрос 1. Что вызывало сомнения перед обменом?", [
        ("a", "Боялся отдать деньги и остаться ни с чем"),
        ("b", "Не понимал, как это вообще работает"),
        ("c", "Переживал за курс — вдруг скрытые комиссии"),
        ("d", "Незнакомый сервис, не знал, можно ли доверять"),
        ("e", "Всё было понятно, не переживал"),
    ]),
    2: ("Вопрос 2. Насколько всё прошло понятно и удобно?", [
        ("a", "Чётко и просто"),
        ("b", "Местами пришлось разбираться"),
        ("c", "Было запутанно"),
    ]),
    3: ("Вопрос 3. Как сработал менеджер?", [
        ("a", "Быстро помог и всё объяснил"),
        ("b", "Помог, но пришлось ждать"),
        ("c", "Отвечал долго или сухо"),
        ("d", "Не помог"),
        ("e", "Не обращался к менеджеру"),
    ]),
    4: ("Вопрос 4. Что для вас было главным при выборе сервиса?", [
        ("a", "Курс"),
        ("b", "Скорость"),
        ("c", "Доверие и отзывы"),
        ("d", "Удобство"),
        ("e", "Совет знакомых"),
    ]),
    5: ("Вопрос 5. Вернётесь / порекомендуете нас?", [
        ("a", "Да"),
        ("b", "Возможно"),
        ("c", "Нет"),
    ]),
}

# краткие подписи для сообщения в канал
LABELS = {
    1: "Сомнения перед обменом",
    2: "Понятно/удобно",
    3: "Менеджер",
    4: "За что выбрали",
    5: "Вернётся/порекомендует",
}

INTRO = "Ваши ответы на пару коротких вопросов — поможет нам стать лучше 🙌"
DOJIM_PROMPT = "Что бы изменило ваш ответ на «да»?"
FREE_PROMPT = ("Что улучшить? Каких услуг не хватает? Напишите своими словами — "
               "можно приложить фото/скриншот.")
THANKS = "Спасибо за вашу обратную связь 🙏"

MEDIA_TYPES = ("photo", "video", "document", "animation", "voice", "video_note", "audio")


class SurveyHandler:
    def __init__(self, bot, state_manager, logger, feedback_chat_id):
        self.bot = bot
        self.state = state_manager
        self.logger = logger
        self.feedback_chat_id = feedback_chat_id

    # -------------------------
    # 📌 REGISTER
    # -------------------------
    def register(self):
        @self.bot.callback_query_handler(func=lambda c: c.data == "survey_start")
        def start(call):
            self.bot.answer_callback_query(call.id)
            self.start_survey(call)

        @self.bot.callback_query_handler(func=lambda c: c.data.startswith("survey/"))
        def handle(call):
            self.bot.answer_callback_query(call.id)
            if call.data == "survey/skip":
                self.finalize(call.message.chat.id)
            else:
                self.handle_answer(call)

    # -------------------------
    # 📌 РЕНДЕР ВОПРОСА (текст + буквы на кнопках)
    # -------------------------
    @staticmethod
    def _q_body(q, with_intro=False):
        text, options = QUESTIONS[q]
        lines = "\n".join(f"{letter}) {opt}" for letter, opt in options)
        body = f"<b>{text}</b>\n\n{lines}"
        return f"{INTRO}\n\n{body}" if with_intro else body

    @staticmethod
    def _q_kb(q):
        kb = InlineKeyboardMarkup()
        kb.row(*[
            InlineKeyboardButton(letter, callback_data=f"survey/{q}/{letter}")
            for letter, _ in QUESTIONS[q][1]
        ])
        return kb

    def _edit(self, chat_id, msg_id, text, reply_markup=None):
        try:
            self.bot.edit_message_text(
                chat_id=chat_id, message_id=msg_id, text=text,
                reply_markup=reply_markup, parse_mode="HTML"
            )
        except Exception as e:
            self.logger.warning(f"survey edit error: {e}")

    # -------------------------
    # 📌 START (одно сообщение на весь опрос)
    # -------------------------
    def start_survey(self, call):
        chat_id = call.message.chat.id
        u = call.from_user
        last = u.last_name or ""
        name = ((u.first_name or "") + (" " + last if last else "")).strip() or "—"

        sent = self.bot.send_message(
            chat_id, self._q_body(1, with_intro=True),
            reply_markup=self._q_kb(1), parse_mode="HTML"
        )

        self.state.set(chat_id, {
            "mode": "survey",
            "msg_id": sent.message_id,
            "answers": {},
            "dojim": None,
            "free_text": None,
            "free_from": None,
            "free_msg_id": None,
            "user_id": u.id,
            "username": u.username,
            "name": name,
        })

    # -------------------------
    # 📌 ОТВЕТЫ Q1..Q5
    # -------------------------
    def handle_answer(self, call):
        chat_id = call.message.chat.id
        st = self.state.get(chat_id)
        if not st or st.get("mode") != "survey":
            return

        try:
            _, q_str, letter = call.data.split("/")
            q = int(q_str)
        except ValueError:
            return

        st["answers"][q] = dict(QUESTIONS[q][1]).get(letter, letter)
        self.state.set(chat_id, st)
        msg_id = st["msg_id"]

        if q < 5:
            nxt = q + 1
            self._edit(chat_id, msg_id, self._q_body(nxt), self._q_kb(nxt))
            return

        # q == 5
        if letter in ("b", "c"):  # «Возможно» / «Нет» — дожим текстом
            self._edit(chat_id, msg_id, DOJIM_PROMPT)
            self.bot.clear_step_handler_by_chat_id(chat_id)
            self.bot.register_next_step_handler_by_chat_id(chat_id, self._got_dojim)
        else:
            self._ask_free(chat_id, msg_id)

    def _got_dojim(self, message):
        chat_id = message.chat.id
        st = self.state.get(chat_id)
        if not st or st.get("mode") != "survey":
            return
        st["dojim"] = (message.text or "").strip() or "—"
        self.state.set(chat_id, st)
        self._ask_free(chat_id, st["msg_id"])

    # -------------------------
    # 📌 ШАГ 6: свободное поле
    # -------------------------
    def _ask_free(self, chat_id, msg_id):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("Пропустить", callback_data="survey/skip"))
        self._edit(chat_id, msg_id, FREE_PROMPT, kb)
        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.bot.register_next_step_handler_by_chat_id(chat_id, self._got_free)

    def _got_free(self, message):
        chat_id = message.chat.id
        st = self.state.get(chat_id)
        if not st or st.get("mode") != "survey":
            return
        st["free_text"] = (message.text or message.caption or "").strip() or None
        if getattr(message, "content_type", "text") in MEDIA_TYPES:
            st["free_from"] = message.chat.id
            st["free_msg_id"] = message.message_id
        self.state.set(chat_id, st)
        self.finalize(chat_id)

    # -------------------------
    # 📌 FINALIZE -> канал
    # -------------------------
    def finalize(self, chat_id):
        st = self.state.get(chat_id)
        if not st or st.get("mode") != "survey":
            return

        self.bot.clear_step_handler_by_chat_id(chat_id)

        a = st["answers"]
        line5 = a.get(5, "—")
        if st.get("dojim"):
            line5 += f" — «{html.escape(st['dojim'])}»"

        # имя — гиперссылка на пользователя (tg://user?id=…)
        name_link = f'<a href="tg://user?id={st["user_id"]}">{html.escape(st["name"])}</a>'
        username = f"@{html.escape(st['username'])}" if st.get("username") else "без username"
        now = datetime.now(MSK).strftime("%d.%m.%Y %H:%M МСК")
        free = html.escape(st["free_text"]) if st.get("free_text") else "—"

        msg = (
            "🆕 Обратная связь\n"
            f"От: {name_link} {username} (id {st['user_id']}) · {now}\n"
            "─────────────\n"
            f"1. {LABELS[1]}: {a.get(1, '—')}\n"
            f"2. {LABELS[2]}: {a.get(2, '—')}\n"
            f"3. {LABELS[3]}: {a.get(3, '—')}\n"
            f"4. {LABELS[4]}: {a.get(4, '—')}\n"
            f"5. {LABELS[5]}: {line5}\n"
            f"💬 Свободно: {free}"
        )

        if self.feedback_chat_id:
            try:
                sent = self.bot.send_message(self.feedback_chat_id, msg, parse_mode="HTML")
                if st.get("free_msg_id"):
                    self.bot.copy_message(
                        chat_id=self.feedback_chat_id,
                        from_chat_id=st["free_from"],
                        message_id=st["free_msg_id"],
                        reply_to_message_id=sent.message_id
                    )
            except Exception as e:
                self.logger.error(f"survey: не отправилось в канал {self.feedback_chat_id}: {e}")
        else:
            self.logger.error("survey: FEEDBACK_CHAT_ID не задан — отзыв никуда не ушёл")

        self._edit(chat_id, st["msg_id"], THANKS)
        self.state.clear(chat_id)
