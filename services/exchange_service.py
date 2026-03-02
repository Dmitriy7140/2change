from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

class ExchangeService:

    def __init__(self, bot, logger, sender_service, fin_instr, state_manager):
        self.bot = bot

        self.finstr = fin_instr()
        self.logger = logger
        self.sender_service = sender_service

        self.state_manager = state_manager

        self.currency_names = {"rub": "<b>RUB🇷🇺</b>",
                               "usd": "<b>USDT🪙</b>",
                               "try": "<b>TRY🇹🇷</b>",
                               "try_cash": "<b>Наличные TRY🇹🇷</b>",
                               "thb": "<b>THB🇹🇭</b>",
                               "thb_cash": "<b>Наличные THB🇹🇭</b>",
                               "cny": "<b>CNY🇨🇳</b>",
                               "krw": "<b>KRW🇰🇷</b>"}
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

        self.min_sum = {"rub/try_cash": "\n• Через банкомат: от <b>10750₽</b>\n"
                                   "• В офисе: от <b>100 000 рублей</b>",
                   "rub/try": "<b>5000₽ (~2500 ₺)</b>",
                   "usd/try_cash": "<b>132 USDT</b>",
                   "usd/try": "<b>70 USDT (~2500₺)</b>",
                   "try/rub": "<b>2000 ₺</b>",
                   "rub/thb_cash": "<b>19390 ₽ (~ 7 000 бат)</b>",
                   "rub/thb": "<b>19390 ₽ (~ 7 000 бат)</b>",
                   "usd/thb_cash": "<b>250 USDT</b>",
                   "usd/thb": "<b>250 USDT</b>",
                   "rub/usd": "<b>30 000₽</b>",
                   "usd/rub": "<b>500 USDT</b>",
                   "rub/cny": "<b>6285₽</b>",
                   "usd/cny": "<b>76 USDT</b>",
                   "cny/rub": "<b>300 CNY</b>",
                   "usd/krw": "<b>214 USDT</b>",
                   "krw/usd": "<b>300.000 KRW</b>",
                   "rub/krw": "<b>17302 RUB</b>",
                   "krw/rub": "<b>300.000 KRW</b>"}

    def register_handlers(self):
        # Главное меню и вызов меню обмена
        @self.bot.callback_query_handler(func=lambda c: c.data.startswith("calc"))
        def send_exchange_menu(call):
            self.send_exchange_main_menu(call)

        @self.bot.callback_query_handler(func=lambda c: c.data.startswith("exchange/"))
        def await_sum_handler(call):
            self.await_sum(call)

        @self.bot.callback_query_handler(func=lambda c: c.data == "convert")
        def send_convert_request_handler(call):
            self.send_convert_request(call)

    def process_amount(self, message):


        chat_id = message.chat.id
        state = self.state_manager.get(chat_id)

        if not state:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("📋Главное меню", callback_data="main_menu"))
            self.bot.send_message(chat_id, "🕘Сессия истекла, попробуйте еще раз.", reply_markup=keyboard)
            return

        currency1 = state["currency1"]
        currency2 = state["currency2"]

        pair = f"{currency1}/{currency2}"
        min_exchange = self.min_amount.get(pair)

        if not min_exchange:
            self.logger.error(f"Нет минимальной пары для {pair}")
            return
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
            return

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
            return


        converted = self.finstr.convert_currencies(int_message, currency1, currency2)
        float_converted = float(converted)
        float_message_text = float(int_message)

        msg = (f"<b>Обмен:</b> {self.currency_names[currency1]} → {self.currency_names[currency2]}\n\n"
               f"<b>Вы отдаете:</b> {int_message} {self.currency_names[currency1]}\n\n"
               f"<b>Вы получаете:</b> {converted} {self.currency_names[currency2]}\n"
               f"<b>Курс: {float_message_text / float_converted if float_converted < float_message_text else float_converted / float_message_text:.2f}</b>\n"
               f"<b>Курс актуален в течении 15 минут!</b>\n\n"
               f"<b>Отправить заявку на обмен?</b>")
        state["amount1"] = int_message
        state["amount2"] = converted
        self.state_manager.set(chat_id, state)

        keybord = InlineKeyboardMarkup(row_width=2)
        keybord.row(InlineKeyboardButton("✅Обменять", callback_data=f"convert"),
                    InlineKeyboardButton("❌Отмена", callback_data="main_menu"))
        self.bot.send_message(chat_id, msg, reply_markup=keybord, parse_mode="HTML")

    def await_sum(self, call):
        self.bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id

        _, currency1, currency2, country = call.data.split("/")
        self.state_manager.clear(chat_id)
        self.state_manager.set(chat_id, {

            'currency1': currency1,
            'currency2': currency2,
            'country': country,
            "amount1": None,
            "amount2": None
        })



        countries_menu = {"1": "tr_menu", "2": "rf_menu", "3": "thai_menu", "4": "cn_menu", "5": "kr_menu"}
        keybord = InlineKeyboardMarkup()
        keybord.add(InlineKeyboardButton("◀️Назад", callback_data=countries_menu[country]))
        msg = (f"✏️ Введите сумму в {self.currency_names[currency1]}\n"
               f"<i>Только цифры - без пробелов, точек и символов</i>\n\n"
               f""
               f"📌 Минимальная сумма: {self.min_sum[f'{currency1}/{currency2}']}")
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