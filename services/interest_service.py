


class InterestService:
    def __init__(self, bot, logger, sheets_interest,qdb, admin_ids):
        self.bot = bot
        self.logger = logger

        self.sheets_interest = sheets_interest
        self.qdb = qdb


        self.ADMIN_IDS = admin_ids


    def register(self):

        @self.bot.message_handler(commands=['change_coef'], func=lambda
        message: message.from_user.id in self.ADMIN_IDS)
        def handle_update_interest(message):
            self.update_interest(message)


    def _get_interest(self) -> dict|None:
        try:
            res = self.sheets_interest.get_interest()
            if not isinstance(res, dict):
                self.logger.error("Таблица наценок вернула не словарь: %r", res)
                return None
            self.logger.info("Получили словарь с наценками")
            return res
        except Exception:
            self.logger.exception("Не удалось получить словарь с наценками")
            return None

    def _set_interest(self, res:dict) -> bool:
        if not isinstance(res, dict):
            self.logger.error("Не удалось применить наценки: получено %r", res)
            return False
        try:
            for name, value in res.items():
                self.qdb.set_coef(name, value/100)
                self.logger.info("Добавили наценки")
            return True
        except Exception:
            self.logger.exception("Не удалось добавить коэффициенты")
            return False

    def update_interest(self, message):
        chat_id = message.chat.id
        res = self._get_interest()
        if isinstance(res, list):
            text = "⛔️При чтении таблицы ошибка со следующими данными:\n" + "\n".join(str(i) for i in res)
            self.bot.send_message(chat_id, text)
            return False
        if res is None:
            self.bot.send_message(chat_id, "⛔️Не удалось прочитать наценки из таблицы. Подробности записаны в лог.")
            return False
        if not self._set_interest(res):
            self.bot.send_message(chat_id, "⛔️Не удалось сохранить наценки. Подробности записаны в лог.")
            return False
        self.bot.send_message(chat_id, "Наценки получили, обновляем базу данных и данные в таблице🕓")
        if not self.insert_currencies_into_table():
            self.bot.send_message(chat_id, "⛔️Курсы не обновлены. Исходная ошибка записана в лог.")
            return False
        self.bot.send_message(chat_id, "Наценки обновили✅\n"
                                       "Актуальные данные:")
        data = self.sheets_interest.fetch_table()

        self.bot.send_message(chat_id, self.form_message(data), parse_mode="HTML")
        return True

    def insert_currencies_into_table(self):
        self.logger.info("Вставляем курсы в гугл таблицу...")
        raw_api_currencies = self.qdb.update_currency()
        if not isinstance(raw_api_currencies, dict):
            self.logger.error("Не получили сырые курсы от API: %r", raw_api_currencies)
            return False
        try:
            self.sheets_interest.set_raw_currencies(raw_api_currencies)
            currencies = self.qdb.get_currencies()
            if not isinstance(currencies, dict):
                self.logger.error("Не получили курсы с наценкой из БД: %r", currencies)
                return False
            self.sheets_interest.set_currencies_with_interest(currencies)
        except Exception:
            self.logger.exception("Не удалось записать курсы в Google-таблицу")
            return False
        return True

    @staticmethod
    def form_message(data):
        result = []
        current_country = None

        for row in data[1:]:  # пропускаем заголовок
            country = row[0]  # A
            markup = row[1]  # B
            pair = row[3]  # D
            value = row[7]  # H

            # пропускаем пустые строки
            if not country and not pair:
                continue

            # новая страна
            if country:
                if current_country != country:
                    current_country = country
                    result.append(f"\n<b>{country}:</b>")

            # строка валют
            if pair and value:
                result.append(f"{pair}: {value} ({markup}%)")

        return "\n".join(result)









