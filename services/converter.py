from datetime import datetime

class FinInstr:
    def __init__(self, qdb, logger):
        # ✅ оставляем только зависимости
        self.qdb = qdb
        self.logger = logger

    # ✅ ЕДИНАЯ точка получения курсов
    def _get_rates(self) -> dict:
        """
        Забираем курсы из БД и сразу превращаем tuple в нормальный dict.
        👉 Это убивает tuple-ад и делает код читаемым.
        """
        raw = self.qdb.get_currencies()

        # если вдруг БД пустая — подстрахуемся
        if not raw:
            self.logger.warning("Курсы не найдены, пробуем обновить...")
            self.qdb.update_currency()
            raw = self.qdb.get_currencies()



        # ✅ превращаем в dict — дальше будет сильно проще
        return raw

    # =========================
    # 💱 ВЫВОД КУРСОВ
    # =========================
    def show_currency(self, country: int) -> str:
        # ✅ каждый раз берем свежие данные
        r = self._get_rates()
        now = datetime.now().strftime("%d-%m-%Y %H:%M")
        """Countries: 1 == Turkey,
         2==Russia, 3== Thailand,
          4== China, 5== korea, 7 == Vietnam, 100 = Bybit Card"""

        if country == 1:
            msg=(f"💱<b> Актуальный курс на {now} </b>\n\n"
                 
                 f"Отдаете:🇷🇺{r["rub_try"]:.2f} RUB\n"
                 f"Получаете:🇹🇷1 TRY (переводом IBAN)\n\n"
                 f""
                 f"Отдаете:🇷🇺{r["cash_rub_try"]:.2f} RUB\n"
                 f"Получаете:🇹🇷1 TRY (наличными лирами)\n\n"
                 f""
                 f"Отдаете:🇹🇷1 TRY\n"
                 f"Получаете:🇷🇺{r["try_rub"]:.2f} RUB\n\n"
                 f""
                 f"Отдаете:🪙1 USDT\n"
                 f"Получаете:🇹🇷{r["usd_try"]:.2f} TRY (Переводом IBAN)\n\n"
                 f""
                 f"Отдаете:🪙1 USDT\n"
                 f"Получаете:🇹🇷{r["cash_usd_try"]:.2f} TRY (Наличными лирами)\n\n"
                 f""
                 f"Отдаете:🪙USDT\n"
                 f"Получаете: Другую валюту (по запросу)\n\n"
                 f""
                 f"<i>⭐️ Акция! При обмене от 20 000 лир через QR — симкарта eSIM на 10ГБ в подарок!</i>\n\n"
                 f"<b>Рассчитайте сумму или оставьте заявку 👇</b>")
            self.logger.info("Сделали сообщение для Турции, выслали!")
            return msg
        elif country == 2:
            msg=(f"💱<b> Актуальный курс на {now} </b>\n\n"
                 f""
                 f"Отдаете:🇷🇺{r["rub_usd"]:.2f} RUB\n"
                 f"Получаете:🪙1 USDT\n\n"
                 f""
                 f"Отдаете:🪙1 USDT\n"
                 f"Получаете:🇷🇺{r["usd_rub"]:.2f} RUB\n\n"
                 f""
                 f"Отдаете:🪙USDT\n"
                 f"Получаете:Другую валюту (по запросу)\n\n"
                 f""
                 f"Отдаете:🇷🇺RUB\n"
                 f"Получаете:Другую валюту (по запросу)"
                 )
            self.logger.info("Сделали сообщение для РФ, выслали!")
            return msg
        elif country == 3:
            msg=(f"💱<b> Актуальный курс на {now} </b>\n\n"
                 f""
                 f"Отдаете:🇷🇺{r["cash_rub_thb"]:.2f} RUB\n"
                 f"Получаете:🇹🇭1 THB (наличными)\n\n"
                 f""
                 f"Отдаете:🇷🇺{r["rub_thb"]:.2f} RUB\n"
                 f"Получаете:🇹🇭1 THB (на счет)\n\n"
                 f""
                 
                 f"Отдаете:🪙1 USDT\n"
                 f"Получаете:🇹🇭{r["cash_usd_thb"]:.2f} THB (наличными)\n\n"
                 f"Отдаете:🪙1 USDT\n"
                 f"Получаете:🇹🇭{r["usd_thb"]:.2f} THB (на счет)\n\n"
                 f""

                 )
            self.logger.info("Сделали сообщение для Тайланда, выслали!")
            return msg
        elif country == 4:
            msg = (f"💱<b>Актуальный курс на {now} </b>\n\n"
                   f""
                   f"Отдаете:🇷🇺{r["rub_cny"]:.2f} RUB\n"
                   f"Получаете:🇨🇳1 CNY\n\n"
                   f""
                   f"Отдаете:🪙1 USDT\n"
                   f"Получаете:🇨🇳{r["usd_cny"]:.2f} CNY\n\n"
                   f""
                   f"Отдаете:🇨🇳1 CNY\n"
                   f"Получаете:🇷🇺{r["cny_rub"]:.2f}RUB\n\n")
            self.logger.info("Сделали сообщение для Китая, выслали!")
            return msg
        elif country == 5:
            msg = (f"<b>Актуальный курс на {now} </b>\n\n"
                   ""
                   f""
                   f"Отдаете: 🇷🇺 1 RUB\n"
                   f"Получаете: 🇰🇷  {r["rub_krw"]:.2f} KRW\n\n"
                   f""
                   f"Отдаете: 🪙1 USDT\n"
                   f"Получаете: 🇰🇷  {r["usd_krw"]:.2f} KRW\n\n"
                   
                   f"Отдаете: 🇰🇷 {r["krw_rub"]:.2f} KRW\n"
                   f"Получаете: 🇷🇺 1 RUB\n\n"
                   f""
                   f"Отдаете: 🇰🇷 {r["krw_usd"]:.2f} KRW\n"
                   f"Получаете: 🪙1 USDT\n\n"
                   f""
                   
                   "Другие валюты - по запросу\n\n"

                   "🎁 При обмене от <b>2 000 000 ₩ — eSIM + 3Гб</b> интернета в подарок!\n\n"

                   "Рассчитайте обмен или оставьте заявку 👇")
            self.logger.info("Сделали сообщение для Кореи, выслали!")
            return msg
        elif country == 7:
            msg = (f"💱<b> Актуальный курс на {now} </b>\n\n"
                   f""
                   f"Отдаете:🇷🇺 1 RUB\n"
                   f"Получаете:🇻🇳 {f'{r["cash_rub_vnd"]:,.2f}'.replace(',',' ')} VND (наличными)\n\n"
                   f"Отдаете:🇷🇺 1 RUB\n"
                   f"Получаете:🇻🇳{f'{r["rub_vnd"]:,.2f}'.replace(',',' ')} VND (на счет)\n\n"
                   f""
                   f"Отдаете:🇻🇳 {f'{1 / r["vnd_rub"]:,.2f}'.replace(',',' ')} VND\n"
                   f"Получаете:🇷🇺 1 RUB\n\n"
                   f""
                   f"Отдаете:🪙1 USDT\n"
                   f"Получаете:🇻🇳 {f'{r["cash_usd_vnd"]:,.2f}'.replace(',',' ')} VND (наличными)\n\n"
                   f"Отдаете:🪙1 USDT\n"
                   f"Получаете:🇻🇳 {f'{r["usd_vnd"]:,.2f}'.replace(',',' ')} VND (на счет)\n\n"
                   f""
                   f"Отдаете:🇷🇺{r["rub_usd"]:.2f} RUB\n"
                   f"Получаете:🪙1 USDT (Bybit Pay)\n\n"

                   )
            self.logger.info("Сделали сообщение для Вьетнама, выслали!")
            return msg
        elif country == 100:
            msg = (f"💱<b> Актуальный курс для пополнения карты Bybit на {now} </b>\n\n"
                   f""
                   f"Отдаете:🇷🇺{r["rub_usd"]:.2f} RUB\n"
                   f"Получаете:🪙1 USDT\n\n")
            return msg


        self.logger.error("Что-то поломалось с отправкой сообщения с курсами!!!")
        return "Что-то пошло не так, попробуйте еще раз..."

    def convert_currencies(
            self,
            amount: float,
            currency1: str,
            currency2: str
    ) -> float | None:

        # ✅ всегда берем свежие курсы
        r = self._get_rates()

        # ✅ нормализуем ввод (на будущее — защита от мусора)
        currency1 = currency1.lower()
        currency2 = currency2.lower()

        # ✅ таблица конвертаций
        rates_map = {
            # ===== USD =====
            ("usd", "rub"): lambda: amount * r["usd_rub"],
            ("usd", "try"): lambda: amount * r["usd_try"],
            ("usd", "try_cash"): lambda: amount * r["cash_usd_try"],
            ("usd", "thb"): lambda: amount * r["usd_thb"],
            ("usd", "thb_cash"): lambda: amount * r["cash_usd_thb"],
            ("usd", "cny"): lambda: amount * r["usd_cny"],
            ("usd", "krw"): lambda: amount * r["usd_krw"],
            ("usd", "vnd"): lambda: amount * r["usd_vnd"],
            ("usd", "vnd_cash"): lambda: amount * r["cash_usd_vnd"],

            # ===== RUB =====
            ("rub", "usd"): lambda: amount / r["rub_usd"],
            ("rub", "try"): lambda: amount / r["rub_try"],
            ("rub", "try_cash"): lambda: amount / r["cash_rub_try"],
            ("rub", "thb"): lambda: amount / r["rub_thb"],
            ("rub", "thb_cash"): lambda: amount / r["cash_rub_thb"],
            ("rub", "cny"): lambda: amount / r["rub_cny"],
            ("rub", "krw"): lambda: amount * r["rub_krw"],
            ("rub", "vnd"): lambda: amount * r["rub_vnd"],
            ("rub", "vnd_cash"): lambda: amount * r["cash_rub_vnd"],

            # ===== CNY =====
            ("cny", "rub"): lambda: amount * r["cny_rub"],

            # ===== VND =====
            ("vnd", "rub"): lambda: amount * r["vnd_rub"],

            # ===== TRY =====
            ("try", "rub"): lambda: amount * r["try_rub"],

            # ===== KRW =====
            ("krw", "rub"): lambda: amount / r["krw_rub"],
            ("krw", "usd"): lambda: amount / r["krw_usd"],
        }

        func = rates_map.get((currency1, currency2))

        if func:
            return func()

        # ✅ логируем, если кейс не покрыт
        self.logger.warning(
            f"Неизвестная конвертация: {currency1} -> {currency2}"
        )

        return None

