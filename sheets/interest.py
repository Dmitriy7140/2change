import gspread


class Interest:
    def __init__(self, logger):
        self.gc = gspread.service_account(filename="sheets/creds.json")
        self.logger = logger
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
        column_data = [
            [format(v, ".2f") if isinstance(v, (int, float)) else v]
            for v in naeb_currencies
        ]
        sheet.update("H2", column_data[1:]) # type: ignore
        self.logger.info("Установили курсы с наценками в гугл док")
        return
    def set_raw_currencies(self, raw_currencies:tuple):
        sheet = self.gc.open("interest").sheet1
        column_data = [
            [format(v, ".2f") if isinstance(v, (int, float)) else v]
            for v in raw_currencies
        ]
        sheet.update("F2", column_data)# type: ignore
        self.logger.info("Установили сырые курсы в гугл док")
        return
    def fetch_table(self):
        return self.gc.open("interest").sheet1.get_all_values()






