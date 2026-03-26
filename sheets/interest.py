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







