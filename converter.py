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
        (self._,
         self.usd_rub,
         self.rub_usd,
         self.usd_try,
         self.rub_try,
         self.cash_rub_try,
         self.try_rub,
         self.usd_thb,
         self.cash_usd_thb,
         self.rub_thb,
         self.cash_rub_thb,
         self.updated_at_str) = raw
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

            (self._,
             self.usd_rub,
             self.rub_usd,
             self.usd_try,
             self.rub_try,
             self.cash_rub_try,
             self.try_rub,
             self.usd_thb,
             self.cash_usd_thb,
             self.rub_thb,
             self.cash_rub_thb,
             self.updated_at_str) = raw
            logger.info("Курсы обновили! Успех!")


    def show_currency(self, country=1):

        if country == 1:
            msg=(f"💱<b> Актуальный курс на сегодняшний день: </b>\n\n"
                 
                 f"Отдаете:🇷🇺{self.rub_try:.2f} RUB\n"
                 f"Получаете:🇹🇷1 TRY (переводом IBAN)\n\n"
                 f""
                 f"Отдаете:🇷🇺{self.cash_rub_try:.2f} RUB\n"
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
                 f"Отдаете:🇷🇺{self.rub_usd:.2f} RUB\n"
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
                 f"Отдаете:🇷🇺{self.rub_thb:.2f} RUB\n"
                 f"Получаете:🇹🇭1 THB (на счет)\n\n"
                 f""
                 f"Отдаете:🇷🇺{self.cash_rub_thb:.2f} RUB\n"
                 f"Получаете:🇹🇭1 THB (наличными)\n\n"
                 f""
                 f"Отдаете:🪙1 USDT\n"
                 f"Получаете:🇹🇭{self.usd_thb:.2f} THB (на счет)\n\n"
                 f""
                 f"Отдаете:🪙1 USDT\n"
                 f"Получаете:🇹🇭{self.cash_usd_thb:.2f} THB (наличными)"
                 )
            logger.info("Сделали сообщение для Тайланда, выслали!")
            return msg
        logger.error("Что-то поломалось с отправкой сообщения с курсами!!!")
        return "Что-то пошло не так, попробуйте еще раз..."
    def convert_currencies(self, amount, currency1, currency2):
        if currency1 == 'usd':
            if currency2 == "rub":
                return amount* self.usd_rub
            elif currency2 == "try":
                return amount * self.usd_try
            elif currency2 == "cash_thb":
                return amount* self.cash_usd_thb
            elif currency2 == "thb":
                return amount * self.usd_thb

        if currency1 == "rub":
            if currency2 == "usd":
                return amount / self.rub_usd
            elif currency2 == "try_cash":
                return amount / self.cash_rub_try
            elif currency2 == "try":
                return amount / self.rub_try
            elif currency2 == 'thb_cash':
                return amount/ self.cash_rub_thb
            elif currency2 == "thb":
                return amount / self.rub_thb

        if currency1 == "try":
            if currency2 == "rub":
                return amount * self.try_rub
if __name__ == '__main__':
    fistr = FinInstr()
    print(fistr.convert_currencies(200, "try", "rub"))




