import gspread


class Interest:
    def __init__(self, logger):
        self.gc = gspread.service_account(filename="sheets/creds.json")
        self.logger = logger

    @staticmethod
    def _fmt_named(name, v):
        """Формат под таблицу (по имени курса, столбцы F/H — только для просмотра).
        vnd_rub (рублей за 1 донг ≈0.003) показываем обратным — донгов за 1 рубль (≈348).
        Прочие мелкие курсы (<1, напр. usd_eur, rub_eur) — с доп. знаками, иначе .2f
        округлит в 0.00. Строки (updated_at) — как есть."""
        if not isinstance(v, (int, float)):
            return v
        if name == "vnd_rub":
            return format(1 / v, ".2f") if v else "0"  # донгов за 1 рубль
        if 0 < abs(v) < 1:
            return format(v, ".4f")
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

    def set_currencies_with_interest(self, marked: dict):
        """marked — словарь курсов с наценкой (из get_currencies), включая updated_at."""
        sheet = self.gc.open("interest").sheet1
        rates = [(k, v) for k, v in marked.items() if k != "updated_at"]
        column_data = [[self._fmt_named(k, v)] for k, v in rates]
        # курсы в H (в порядке ключей = порядок строк в таблице), пустая ячейка
        # затирает старую дату под списком, а сам updated_at кладём в I2
        payload = column_data + [[""]]
        sheet.update("H2", payload) # type: ignore
        sheet.update("I2", [[marked.get("updated_at", "")]])  # время последнего обновления
        self.logger.info("Установили курсы с наценками в гугл док")
        return
    def set_raw_currencies(self, raw: dict):
        """raw — словарь сырых курсов (из update_currency)."""
        sheet = self.gc.open("interest").sheet1
        column_data = [[self._fmt_named(k, v)] for k, v in raw.items()]
        sheet.update("F2", column_data)# type: ignore
        self.logger.info("Установили сырые курсы в гугл док")
        return
    def fetch_table(self):
        return self.gc.open("interest").sheet1.get_all_values()






