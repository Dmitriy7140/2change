import gspread


class Interest:
    def __init__(self, logger):
        self.gc = gspread.service_account(filename="sheets/creds.json")
        self.logger = logger

    @staticmethod
    def _fmt(v):
        """Числа форматируем под таблицу. Мелкий курс (<1 — это только vnd_rub≈0.003,
        рублей за 1 донг) показываем как обратный — донгов за 1 рубль (≈348), иначе .2f
        округлил бы в 0.00. Столбцы F/H только для просмотра, бот их обратно не читает."""
        if not isinstance(v, (int, float)):
            return v
        if 0 < abs(v) < 1:
            return format(1 / v, ".2f")  # донгов за 1 рубль
        return format(v, ".2f")
    def get_interest(self):
        sheet = self.gc.open("interest").sheet1
        interest = sheet.col_values(2)[1:]
        names = sheet.col_values(11)[1:]
        zipped = zip(interest, names)
        res = {}
        errors=[]
        for num, name in zipped:
            if num == "" or name == "":
                continue
            try:
                if "," in num:
                    num = num.replace(",",".")
                res[name] = float(num)

            except ValueError:
                errors.append(num)
        self.logger.info("Считали наценки из таблицы")
        if errors:
            self.logger.error("Есть ошибки в таблице")
        return errors if errors else res

    def set_currencies_with_interest(self, naeb_currencies:tuple):
        sheet = self.gc.open("interest").sheet1
        column_data = [[self._fmt(v)] for v in naeb_currencies]
        # пишем без id (первый) и без updated_at (последний) — таймстамп в таблицу не нужен;
        # пустая ячейка в конце затирает старую дату, оставшуюся от прошлых записей
        payload = column_data[1:-1] + [[""]]
        sheet.update("H2", payload) # type: ignore
        self.logger.info("Установили курсы с наценками в гугл док")
        return
    def set_raw_currencies(self, raw_currencies:tuple):
        sheet = self.gc.open("interest").sheet1
        column_data = [[self._fmt(v)] for v in raw_currencies]
        sheet.update("F2", column_data)# type: ignore
        self.logger.info("Установили сырые курсы в гугл док")
        return
    def fetch_table(self):
        return self.gc.open("interest").sheet1.get_all_values()






