from database_main import QueueDB
from datetime import datetime
from utils import logger
qdb = QueueDB()


class FinInstr:
    def __init__(self,raw=qdb.get_currencies()):

        if not raw:
            logger.error("Финансист курсы не принял, колонка пустая!!!")
            qdb.update_currency()
            raw=qdb.get_currencies()
            if raw:
                logger.info("Финансист все порешал!")


        self._, self.usd_rub, self.usd_thb, self.usd_try, self.try_rub, self.thb_rub, self.thb_try, self.updated_at_str = raw
        logger.info("Финансист курсы принял...")

        updated_at = datetime.strptime(self.updated_at_str, "%d-%m-%Y %H:%M:%S")
        logger.info("Конвертируем время...")

        # Текущее время
        now = datetime.now()
        logger.info(f"Сейчас {now}, последнее обновление было {self.updated_at_str}...")

        # Разница во времени
        time_diff = now - updated_at
        logger.info(f"С последнего обновления курсов прошло {time_diff.total_seconds()} секунд...")
        if time_diff.total_seconds() > 7200:
            logger.info("Обновляем курсы...")
            qdb.update_currency()
            raw = qdb.get_currencies()

            self._, self.usd_rub, self.usd_thb, self.usd_try, self.try_rub, self.thb_rub, self.thb_try, self.updated_at_str = raw
            logger.info("Курсы обновили! Успех!")


    def show_currency(self, country=1):

        if country == 1:
            msg=(f"💱<b> Актуальный курс на сегодняшний день: </b>\n\n"
                 f"БЕЗ НАЦЕНКИ\n\n"
                 f""
                 f"Отдаете:🇷🇺{self.try_rub:.2f} RUB\n"
                 f"Получаете:🇹🇷1 TRY (переводом IBAN)\n\n"
                 f""
                 f"Отдаете:🇷🇺{self.try_rub:.2f} RUB\n"
                 f"Получаете:🇹🇷1 TRY (наличными лирами)\n\n"
                 f""
                 f"Отдаете:🇹🇷1 TRY\n"
                 f"Получаете:🇷🇺{self.try_rub:.2f} RUB\n\n"
                 f""
                 f"Отдаете:🪙1 USDT\n"
                 f"Получаете:🇹🇷{self.usd_try:.2f} TRY\n\n"
                 f""
                 f"Отдаете:🪙USDT\n"
                 f"Получаете: Другую валюту (по запросу)\n\n"
                 f""
                 f"<i>⭐️ Акция! При обмене от 20 000 лир через QR — симкарта eSIM на 10ГБ в подарок!</i>\n\n"
                 f"<b>Рассчитайте сумму или оставьте заявку 👇</b>")
            logger.info("Сделали сообщение для Турции, выслали!")
            return msg
        elif country == 2:
            msg=(f"💱<b> Актуальный курс на сегодняшний день: </b>\n\n"
                 f""
                 f"Отдаете:🇷🇺{self.usd_rub:.2f} RUB\n"
                 f"Получаете:🪙1 USDT\n\n"
                 f""
                 f"Отдаете:🪙1 USDT\n"
                 f"Получаете:🇷🇺{self.usd_rub:.2f} RUB\n\n"
                 f""
                 f"Отдаете:🪙USDT\n"
                 f"Получаете:Другую валюту (по запросу)\n\n"
                 f""
                 f"Отдаете:🇷🇺RUB\n"
                 f"Получаете:Другую валюту (по запросу)"
                 )
            logger.info("Сделали сообщение для РФ, выслали!")
            return msg

        elif country == 3:
            msg=(f"💱<b> Актуальный курс на сегодняшний день: </b>\n\n"
                 f""
                 f"Отдаете:🇷🇺{self.thb_rub:.2f} RUB\n"
                 f"Получаете:🇹🇭1 THB (на счет)\n\n"
                 f""
                 f"Отдаете:🇷🇺{self.thb_rub:.2f} RUB\n"
                 f"Получаете:🇹🇭1 THB (наличными)\n\n"
                 f""
                 f"Отдаете:🪙1 USDT\n"
                 f"Получаете:🇹🇭{self.usd_thb:.2f} THB (на счет)\n\n"
                 f""
                 f"Отдаете:🪙1 USDT\n"
                 f"Получаете:🇹🇭{self.usd_thb:.2f} THB (наличными)"
                 )
            logger.info("Сделали сообщение для Тайланда, выслали!")
            return msg
        logger.error("Что-то поломалось с отправкой сообщения с курсами!!!")
        return "Что-то пошло не так, попробуйте еще раз..."
    def convert_currencies(self, amount, currency1, currency2):
        """Указываем одну из валют:
        try,try_cash
        usd,
        thb,thb_cash
        rub,"""
        amount = amount
        currency1 = currency1
        currency2 = currency2

        if currency1.lower()=="usd":
            if currency2.lower()=="thb":

                return amount *
            if currency2.lower()=="thb_cash":
                return amount*self.usd_thb * (1+ we_sell["cash_usd_thb_c"])
            if currency2.lower()=="try":

                return amount* self.usd_try *(1+ we_sell["usd_try_c"])
            if currency2.lower()=="rub":

                return amount * self.usd_rub * (1 + we_sell["usd_rub_c"])
        #


        if currency1.lower()=="rub":
            if currency2.lower()=="try":#ибан
                return amount * self.try_rub * (1 + we_sell["try_rub_c"])
            if currency2.lower()=="try_cash":
                return amount * self.try_rub * (1 + we_sell["cash_try_rub_c"])
            if currency2.lower()=="thb":
                return amount * self.thb_rub * (1 + we_sell["thb_rub_c"])
            if currency2.lower()=="thb_cash":
                return amount* self.thb_rub * (1 + we_sell["cash_thb_rub_c"])
            if currency2.lower()=="usd":
                return amount*self.usd_rub * (1+ we_buy["usd_rub_c"])



        return None

if __name__ == '__main__':
    fistr = FinInstr()
    print(fistr.convert_currencies(200, "usd", "thb"))




