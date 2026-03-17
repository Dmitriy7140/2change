from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

class ExchangeService:

    def __init__(self, bot, logger, sender_service, fin_instr, state_manager):
        self.bot = bot

        self.finstr = fin_instr()
        self.logger = logger
        self.sender_service = sender_service

        self.state_manager = state_manager

        self.currency_names = {"rub": "RUB🇷🇺",
                               "usd": "USDT🪙",
                               "try": "TRY🇹🇷",
                               "try_cash": "нал. TRY🇹🇷",
                               "thb": "THB🇹🇭",
                               "thb_cash": "нал. THB🇹🇭",
                               "cny": "CNY🇨🇳",
                               "krw": "KRW🇰🇷"}
        self.min_amount = {"rub/try_cash": 10750,
                      "rub/try": 5000,
                      "usd/try_cash": 132,
                      "usd/try": 70,
                      "try/rub": 2000,
                      "rub/thb_cash": 19390,
                      "rub/thb": 19390,
                      "usd/thb_cash": 250,
                      "usd/thb": 250,
                      "rub/usd": 30000,
                      "usd/rub": 500,
                      "rub/cny": 6285,
                      "usd/cny": 76,
                      "cny/rub": 300,
                      "krw/rub": 300000,
                      "krw/usd": 300000,
                      "usd/krw": 214,
                      "rub/krw": 17302}
        self.min_amount_reversed = {"rub/try_cash": 6000,
                           "rub/try": 3000,
                           "usd/try_cash": 6000,
                           "usd/try": 3000,
                           "try/rub": 4000,
                           "rub/thb_cash": 8000,
                           "rub/thb": 8000,
                           "usd/thb_cash": 8000,
                           "usd/thb": 8000,
                           "rub/usd": 350,
                           "usd/rub": 40000,
                           "rub/cny": 550,
                           "usd/cny": 550,
                           "cny/rub": 3500,
                           "krw/rub": 16500,
                           "krw/usd": 205,
                           "usd/krw": 300000,
                           "rub/krw": 300000}


        self.historical_pairs = {"usd/rub":True,
                                 "rub/usd":False,
                                 "rub/try_cash": False,
                                  "rub/try": False,
                                  "usd/try_cash": True,
                                  "usd/try": True,
                                  "try/rub": True,
                                  "rub/thb_cash": False,
                                  "rub/thb": False,
                                  "usd/thb_cash":True,
                                  "usd/thb":True,

                                  "rub/cny": False,
                                  "usd/cny":True,
                                  "cny/rub":True,
                                  "usd/krw":True,
                                  "krw/usd":False,
                                  "rub/krw":True,
                                  "krw/rub":False }
                                #true если второй валюты как правило больше чем первой при конвертации

    def register_handlers(self):
        # Главное меню и вызов меню обмена
        @self.bot.callback_query_handler(func=lambda c: c.data.startswith("calc"))
        def send_exchange_menu(call):
            self.send_exchange_main_menu(call)

        @self.bot.callback_query_handler(func=lambda c: c.data.startswith("exchange/"))
        def await_mode_handler(call):
            self.await_mode(call)

        @self.bot.callback_query_handler(func=lambda c: c.data == "convert")
        def send_convert_request_handler(call):
            self.send_convert_request(call)
        @self.bot.callback_query_handler(func=lambda c: c.data.startswith("await_sum/"))
        def await_sum_handler(call):
            self.await_sum(call)

    def process_amount(self, message):


        chat_id = message.chat.id
        state = self.state_manager.get(chat_id)

        if not state:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("📋Главное меню", callback_data="main_menu"))
            self.bot.send_message(chat_id, "🕘Сессия истекла, попробуйте еще раз.", reply_markup=keyboard)
            return None

        currency1 = state["currency1"]
        currency2 = state["currency2"]
        mode = state["mode"]
        pair = f"{currency1}/{currency2}"


        int_message = self.check_message(message, mode, pair, currency1, currency2)
        if int_message:
            converted = self.finstr.convert_currencies(int_message, currency1, currency2)


            k = int_message / converted if converted < int_message else converted / int_message
            if mode == "get":

                if self.historical_pairs[pair]:
                    converted /= k
                    converted /= k



                elif not self.historical_pairs[pair]:
                    converted *=k
                    converted *= k
            elif mode == "give" and currency2.endswith("_cash") :
                converted_rounded = self.round_to_thousand(int(converted))
                int_message = converted_rounded / k if converted > int_message else converted_rounded * k
                converted = converted_rounded


            msg = (f"<b>Обмен:</b> {self.currency_names[currency1]} → {self.currency_names[currency2]}\n\n"
                   f"<b>Вы отдаете:</b> {converted if mode == "get" else int_message:.0f} {self.currency_names[currency1]}\n\n"
                   f"<b>Вы получаете:</b> {int_message if mode == "get" else converted:.0f} {self.currency_names[currency2]}\n"
                   f"<b>Курс: {k:.2f}</b>\n"
                   f"<b>Курс актуален в течении 15 минут!</b>\n\n"
                   f"<b>Отправить заявку на обмен?</b>")
            state["amount1"] = f"{converted if mode == "get" else int_message:.0f}"
            state["amount2"] = f"{int_message if mode == "get" else converted:.0f}"
            self.state_manager.set(chat_id, state)

            keybord = InlineKeyboardMarkup(row_width=2)
            keybord.row(InlineKeyboardButton("✅Обменять", callback_data=f"convert"),
                        InlineKeyboardButton("❌Отмена", callback_data="main_menu"))
            self.bot.send_message(chat_id, msg, reply_markup=keybord, parse_mode="HTML")
            return None
        return None
    def check_message(self, message, mode, pair, currency1,currency2) -> int|None:
        chat_id = message.chat.id
        min_exchange = self.min_amount_reversed.get(pair) if mode == "get" else self.min_amount.get(pair)
        if not min_exchange:
            self.logger.error(f"Нет минимальной пары для {pair}")
            return None
        try:
            int_message = int(message.text.replace(" ", ""))
        except ValueError:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("📋Главное меню", callback_data="main_menu"))
            self.bot.send_message(chat_id, "❌Введите, пожалуйста, целое число.", reply_markup=keyboard)

            self.bot.clear_step_handler_by_chat_id(chat_id)
            self.bot.register_next_step_handler_by_chat_id(
                chat_id,
                self.process_amount
            )
            return None


        if mode == "get":


            if int_message < min_exchange:
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton("📋Главное меню", callback_data="main_menu"))
                self.bot.send_message(
                    chat_id,
                    f"<b>❌Минимальная сумма: {min_exchange} {self.currency_names[currency2]}</b>",
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                self.bot.clear_step_handler_by_chat_id(chat_id)
                self.bot.register_next_step_handler_by_chat_id(
                    chat_id,
                    self.process_amount
                )
                return None
        else:

            if int_message < min_exchange:
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton("📋Главное меню", callback_data="main_menu"))
                self.bot.send_message(
                    chat_id,
                    f"❌Минимальная сумма: <b>{min_exchange} {self.currency_names[currency1]}</b>",
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                self.bot.clear_step_handler_by_chat_id(chat_id)
                self.bot.register_next_step_handler_by_chat_id(
                    chat_id,
                    self.process_amount
                )
                return None
        return self.round_to_thousand(int_message) if mode == "get" and currency2.endswith("_cash") else int_message

    def await_mode(self, call):
        self.bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id

        _, currency1, currency2, country = call.data.split("/")
        msg = ("⚙️Выберите режим калькулятора:\n\n"
               f"<b>Обмен : {self.currency_names[currency1]} → {self.currency_names[currency2]}\n\n</b>"
               ""
              f"1. Укажу, сколько хочу получить {self.currency_names[currency2]}\n"
              f"2. Укажу, сколько отдам {self.currency_names[currency1]}")
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(InlineKeyboardButton(f"Получу {self.currency_names[currency2]}", callback_data="await_sum/get"))
        kb.add(InlineKeyboardButton(f"Отдам {self.currency_names[currency1]}", callback_data="await_sum/give"))
        self.bot.send_message(chat_id, msg, reply_markup=kb, parse_mode="HTML")
        self.state_manager.clear(chat_id)
        self.state_manager.set(chat_id, {

            'currency1': currency1,
            'currency2': currency2,
            'country': country,
            "amount1": None,
            "amount2": None,
            "mode":None

        })




    def await_sum(self,call):

        self.bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        _, mode = call.data.split("/")

        state= self.state_manager.get(chat_id)

        currency1 = state["currency1"]
        currency2 = state["currency2"]
        country = state["country"]
        countries_menu = {"1": "tr_menu", "2": "rf_menu", "3": "thai_menu", "4": "cn_menu", "5": "kr_menu"}
        self.state_manager.set(chat_id, {

            'currency1': currency1,
            'currency2': currency2,
            'country': country,
            "amount1": None,
            "amount2": None,
            "mode": mode

        })
        warning = (
            "⚠️При обмене на наличные деньги введенная сумма пересчитывается так, "
            "чтобы получаемая сумма была кратна 1000\n\n"
            "💡Например, Вы хотите обменять 75 USDT в лиры и должны получить 7 236 лир. "
            "Банкомат такую сумму не выдаст. Калькулятор в заявке округлит до 70 USDT, "
            "что составит 7000 лир\n\n"
        ) if currency2.endswith("_cash") else ""
        if mode == "give":

            min_sum = f"{self.min_amount[f"{currency1}/{currency2}"]} {self.currency_names[currency1]}"


            keybord = InlineKeyboardMarkup()
            keybord.add(InlineKeyboardButton("◀️Назад", callback_data=countries_menu[country]))
            msg = (f"✏️ Введите сумму в {self.currency_names[currency1]}\n"
                   f"<i>Только цифры - без пробелов, точек и символов</i>\n\n"
                   f"{warning}"
                   f"📌 Минимальная сумма: <b>{min_sum}\n</b>")
            self.bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keybord)

            self.bot.clear_step_handler_by_chat_id(chat_id)
            self.bot.register_next_step_handler_by_chat_id(
                chat_id,
                self.process_amount
            )
        elif mode == "get":

            min_sum = f"{self.min_amount_reversed[f"{currency1}/{currency2}"]} {self.currency_names[currency2]}"

            keybord = InlineKeyboardMarkup()
            keybord.add(InlineKeyboardButton("◀️Назад", callback_data=countries_menu[country]))

            msg = (
                f"✏️ Введите сумму в {self.currency_names[currency2]}\n"
                f"<i>Только цифры - без пробелов, точек и символов</i>\n\n"
                f"{warning}\n"
                f"<b>Укажите, сколько {self.currency_names[currency2]} вы хотите получить</b>\n\n"
                f"📌Минимальная сумма: <b>{min_sum}\n</b>"
            )

            self.bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keybord)

            self.bot.clear_step_handler_by_chat_id(chat_id)
            self.bot.register_next_step_handler_by_chat_id(
                chat_id,
                self.process_amount
            )

        return

    def send_convert_request(self, call):
        self.bot.answer_callback_query(call.id)

        user_id = call.from_user.id
        user_ref = call.from_user.username
        chat_id = call.message.chat.id
        last_name = call.from_user.last_name or ""
        user_name = (call.from_user.first_name or "") + (" " + last_name if last_name else "")
        if call.data == "convert":
            app_state = self.state_manager.get(chat_id)
            if not app_state:
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton("📋Главное меню", callback_data="main_menu"))
                self.bot.send_message(chat_id, "🕘Сессия истекла, попробуйте еще раз.", reply_markup=keyboard)
                return
            currency1, currency2, country, amount1, amount2 = app_state["currency1"], app_state["currency2"], app_state[
                "country"], app_state["amount1"], app_state["amount2"]

            self.sender_service.send_application(user_id=user_id, user_name=user_name, user_ref=user_ref, chat_id=chat_id,
                                            amount1=amount1, amount2=amount2, country=country,
                                            currency1=self.currency_names[currency1], currency2=self.currency_names[currency2])
            self.state_manager.clear(chat_id)

            return

    def send_exchange_main_menu(self, call):
        self.bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        if call.data == "calc_rf":
            msg = "💸<i>Выберите валюту для обмена:</i>"
            keybord1 = InlineKeyboardMarkup(row_width=2)
            keybord1.row(InlineKeyboardButton("🪙USDT→🇷🇺", callback_data="exchange/usd/rub/2"),
                         InlineKeyboardButton("🇷🇺→🪙USDT", callback_data="exchange/rub/usd/2"))
            keybord1.row(InlineKeyboardButton("💰Иные валюты (менеджер)", callback_data="request/💰Обмен иных валют/2"),
                         InlineKeyboardButton("◀️Назад", callback_data="rf_menu"))
            self.bot.send_message(chat_id, msg, reply_markup=keybord1, parse_mode="HTML")
        elif call.data == "calc_thai":
            msg = "💸<i>Выберите валюту для обмена:</i>"
            keybord2 = InlineKeyboardMarkup(row_width=2)
            keybord2.row(InlineKeyboardButton("🪙USDT→🇹🇭 (Переводом)", callback_data="exchange/usd/thb/3"),
                         InlineKeyboardButton("🪙USDT→🇹🇭 (Наличные)", callback_data="exchange/usd/thb_cash/3"))

            keybord2.row(InlineKeyboardButton("🇷🇺→🇹🇭 (Переводом)", callback_data="exchange/rub/thb/3"),
                         InlineKeyboardButton("🇷🇺→🇹🇭 (Наличные)", callback_data="exchange/rub/thb_cash/3"))
            keybord2.row(InlineKeyboardButton("💰Иные валюты (менеджер)", callback_data="request/💰Обмен иных валют/3"),
                         InlineKeyboardButton("◀️Назад", callback_data="thai_menu"))
            self.bot.send_message(chat_id, msg, reply_markup=keybord2, parse_mode="HTML")
        elif call.data == "calc_tr":
            msg = "💸<i>Выберите валюту для обмена:</i>"
            keybord3 = InlineKeyboardMarkup(row_width=2)
            keybord3.row(InlineKeyboardButton("🇷🇺→🇹🇷 (IBAN)", callback_data="exchange/rub/try/1"),
                         InlineKeyboardButton("🇷🇺→🇹🇷 (Наличные)", callback_data="exchange/rub/try_cash/1"))

            keybord3.row(InlineKeyboardButton("🪙USDT→🇹🇷 (IBAN)", callback_data="exchange/usd/try/1"),
                         InlineKeyboardButton("🪙USDT→🇹🇷 (Наличные)", callback_data="exchange/usd/try_cash/1"))

            keybord3.add(InlineKeyboardButton("🇹🇷→🇷🇺 (Переводом)", callback_data="exchange/try/rub/1"))
            keybord3.row(InlineKeyboardButton("💰Иные валюты (менеджер)", callback_data="request/💰Обмен иных валют/1"),
                         InlineKeyboardButton("◀️Назад", callback_data="tr_menu"))
            self.bot.send_message(chat_id, msg, reply_markup=keybord3, parse_mode="HTML")
        elif call.data == "calc_cn":
            msg = "💸<i>Выберите валюту для обмена:</i>"
            keybord4 = InlineKeyboardMarkup()
            keybord4.add(InlineKeyboardButton("🇷🇺→🇨🇳CNY (юань)", callback_data="exchange/rub/cny/4"), )
            keybord4.add(InlineKeyboardButton("🪙USDT→🇨🇳CNY (юань)", callback_data="exchange/usd/cny/4"))
            keybord4.add(InlineKeyboardButton("🇨🇳CNY (юань)→🇷🇺", callback_data="exchange/cny/rub/4"))
            keybord4.row(InlineKeyboardButton("💰Иные валюты (менеджер)", callback_data="request/💰Обмен иных валют/4"),
                         InlineKeyboardButton("◀️Назад", callback_data="cn_menu"))
            self.bot.send_message(chat_id, msg, reply_markup=keybord4, parse_mode="HTML")
        elif call.data == "calc_kr":
            msg = ("<i>Выберите валюту для обмена:</i>\n\n"
                   "<b>🎁 При обмене от 2 000 000₩ – eSIM +3 ГБ в подарок!</b>")
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("🇰🇷 KRW (нал/перевод) → 🇷🇺RUB", callback_data="exchange/krw/rub/5"))
            kb.add(InlineKeyboardButton("🇰🇷 KRW (нал/перевод) → 🪙 USDT", callback_data="exchange/krw/usd/5"))
            kb.add(InlineKeyboardButton("🇷🇺RUB → 🇰🇷 KRW (нал/счет)", callback_data="exchange/rub/krw/5"))
            kb.add(InlineKeyboardButton("🪙 USDT → 🇰🇷 KRW (нал/счет)", callback_data="exchange/usd/krw/5"))
            kb.row(InlineKeyboardButton("💰Иные валюты (менеджер)", callback_data="request/💰Обмен иных валют/5"),
                   InlineKeyboardButton("◀️Назад", callback_data="kr_menu"))
            self.bot.send_message(chat_id, msg, reply_markup=kb, parse_mode="HTML")
        return

    @staticmethod
    def round_to_thousand( n: int) -> int:
        remainder = n % 1000

        if remainder < 500:
            return n - remainder
        else:
            return n + (1000 - remainder)

