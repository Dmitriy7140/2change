from database_main import QueueDB

from datetime import datetime
from utils import logger
qdb = QueueDB()


class FinInstr:
    def __init__(self):
        raw = qdb.get_currencies()
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
         self.cash_usd_try,
         self.rub_try,
         self.cash_rub_try,
         self.try_rub,
         self.usd_thb,
         self.cash_usd_thb,
         self.rub_thb,
         self.cash_rub_thb,
         self.rub_cny,
         self.usd_cny,
         self.cny_rub,
         self.usd_krw ,
         self.krw_usd ,
         self.rub_krw ,
         self.krw_rub,
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
             self.cash_usd_try,
             self.rub_try,
             self.cash_rub_try,
             self.try_rub,
             self.usd_thb,
             self.cash_usd_thb,
             self.rub_thb,
             self.cash_rub_thb,
             self.rub_cny,
             self.usd_cny,
             self.cny_rub,
             self.usd_krw,
             self.krw_usd,
             self.rub_krw,
             self.krw_rub,
             self.updated_at_str) = raw
            logger.info("Курсы обновили! Успех!")


    def show_currency(self, country=1):
        """Countries: 1 == Turkey,
         2==Russia, 3== Thailand,
          4== China, 5== korea"""
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
                 f"Получаете:🇹🇷{self.usd_try:.2f} TRY (Переводом IBAN)\n\n"
                 f""
                 f"Отдаете:🪙1 USDT\n"
                 f"Получаете:🇹🇷{self.cash_usd_try:.2f} TRY (Наличными лирами)\n\n"
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
        elif country == 4:
            msg = (f"💱<b> Актуальный курс на сегодняшний день: </b>\n\n"
                   f""
                   f"Отдаете:🇷🇺{self.rub_cny:.2f} RUB\n"
                   f"Получаете:🇨🇳1 CNY\n\n"
                   f""
                   f"Отдаете:🪙1 USDT\n"
                   f"Получаете:🇨🇳{self.usd_cny:.2f} CNY\n\n"
                   f""
                   f"Отдаете:🇨🇳1 CNY\n"
                   f"Получаете:🇷🇺{self.cny_rub:.2f}RUB\n\n")
            return msg
        elif country == 5:
            msg = ("<b>Актуальный курс на сегодняшний день: </b>\n\n"
                   ""
                   f"Отдаете: 🪙1 USDT\n"
                   f"Получаете: 🇰🇷  {self.usd_krw:.2f} KRW\n\n"
                   f""
                   f"Отдаете: 🇷🇺 1 RUB\n"
                   f"Получаете: 🇰🇷  {self.rub_krw:.2f} KRW\n\n"
                   f""
                   f"Отдаете: 🇰🇷 {self.krw_rub:.2f} KRW\n"
                   f"Получаете: 🇷🇺 1 RUB\n\n"
                   f""
                   f"Отдаете: 🇰🇷 {self.krw_usd:.2f} KRW\n"
                   f"Получаете:🪙 1 USDT\n\n"
                   f""
                   
                   "🪙 USDT/ 🇷🇺 RUB/другие валюты - по запросу\n\n"

                   "🎁 При обмене от <b>2 000 000 ₩ — eSIM + 3Гб</b> интернета в подарок!\n\n"

                   "Рассчитайте обмен или оставьте заявку 👇")
            return msg
        logger.error("Что-то поломалось с отправкой сообщения с курсами!!!")
        return "Что-то пошло не так, попробуйте еще раз..."
    def convert_currencies(self, amount, currency1, currency2):
        if currency1 == 'usd':
            if currency2 == "rub":
                return f"{amount* self.usd_rub:.2f}"
            elif currency2 == "try":
                return f"{amount * self.usd_try:.2f}"
            elif currency2 == "try_cash":
                return f"{amount* self.cash_usd_try:.2f}"

            elif currency2 == "thb":
                return f"{amount * self.usd_thb:.2f}"
            elif currency2 == "thb_cash":
                return f"{amount* self.cash_usd_thb:.2f}"

            elif currency2 == "cny":
                return f"{amount* self.usd_cny:.2f}"
            elif currency2 == "krw":
                return f"{amount* self.usd_krw:.2f}"

        if currency1 == "rub":
            if currency2 == "usd":
                return f"{amount / self.rub_usd:.2f}"
            elif currency2 == "try_cash":
                return f"{amount / self.cash_rub_try:.2f}"
            elif currency2 == "try":
                return f"{amount / self.rub_try:.2f}"
            elif currency2 == 'thb_cash':
                return f"{amount/ self.cash_rub_thb:.2f}"
            elif currency2 == "thb":
                return f"{amount / self.rub_thb:.2f}"
            elif currency2 == "cny":
                return f"{amount / self.rub_cny:.2f}"
            elif currency2 == "krw":
                return f"{amount * self.rub_krw:.2f}"
        if currency1 == "cny":
            if currency2 == "rub":
                return f"{amount * self.cny_rub:.2f}"

        if currency1 == "try":
            if currency2 == "rub":
                return f"{amount * self.try_rub:.2f}"
            return None
        if currency1 == "krw":
            if currency2 == "rub":
                return f"{amount / self.krw_rub:.2f}"
            elif currency2 == "usd":
                return f"{amount / self.krw_usd:.2f}"
        return None
if __name__ == '__main__':
    fistr = FinInstr()
    print(fistr.convert_currencies(10, "rub", "krw"))




