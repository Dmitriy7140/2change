from database_main import QueueDB
from datetime import datetime

qdb = QueueDB()


class FinInstr:
    def __init__(self,row=qdb.get_currencies()):

        self._, self.usd_rub, self.usd_thb, self.usd_try, self.self.updated_at_str = row

        updated_at = datetime.strptime(self.updated_at_str, "%d-%m-%Y %H:%M:%S")

        # Текущее время
        now = datetime.now()

        # Разница во времени
        time_diff = now - updated_at
        if time_diff.total_seconds() > 7200:
            row = qdb.update_currency()
            self._, self.usd_rub, self.usd_thb, self.usd_try, self.updated_at_str = row
        self.rub_try=self.usd_rub/self.usd_try
        self.rub_thb=self.usd_rub/self.usd_thb

    def show_currency(self):
        msg=(f"💱<b> Курсы на {self.updated_at_str} </b>\n\n"
             f"Вы отдаете = Вы получаете(без наценки)\n\n"
             
             # f"{self.rub_try:.2f} RUB = 1 TRY (наличными)\n"
             # f"{self.rub_try:.2f} RUB = 1 TRY (переводом Iban)\n"
             # f"1 TRY = {self.rub_try:.2f} RUB\n\n"
             f"1 USDT = {self.usd_try:.2f} TRY\n"
             f"1 USDT = {self.usd_thb:.2f} THB\n"
             f"1 USDT = {self.usd_rub:.2f} RUB (курс апи)\n"
             f"Вы отдаете = Вы получаете(С наценкой)\n\n"

             # f"{self.rub_try+(self.rub_try*0.04):.2f} RUB = 1 TRY (наличными)+3%\n"
             # f"{self.rub_try+(self.rub_try*0.03):.2f} RUB = 1 TRY (переводом Iban)+3%\n"
             # f"1 TRY = {self.rub_try-(self.rub_try*0.03):.2f} RUB-3%\n\n"
             f"1 USDT = {self.usd_try+(self.usd_try*0.03):.2f} TRY+3%\n"
             f"1 USDT = {self.usd_thb+(self.usd_thb*0.03):.2f} THB+3%\n"
             f"1 USDT = {self.usd_rub+(self.usd_rub*0.03):.2f} RUB+3%\n"
             )
        return msg
