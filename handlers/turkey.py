from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Callable


class TurkeyHandlers:

    def __init__(self, bot, subscription_service, send_media, fin_instr_class_obj, state_manager):
        self.bot = bot
        self.subscription_service = subscription_service
        self.send_media = send_media
        self.finstr = fin_instr_class_obj
        self.clearstate = state_manager.clear

        self.routes : dict[str, Callable] = {
            "tr_menu": self.tr_menu,
            "tr_card_menu": self.tr_card_menu,
            "tr_qr_menu": self.tr_qr_menu,
            "tr_iban_menu": self.tr_iban_menu,
            "tr_office_cash_menu": self.tr_office_cash_menu,
            "tr_cash_transactions_menu": self.tr_cash_transactions_menu,
            "tr_acc": self.tr_acc,
            "tr_services_booking_menu": self.tr_services_booking_menu,
            "tr_currency_menu": self.tr_currency_menu,
        }

    def register(self):
        @self.bot.callback_query_handler(lambda c: c.data.startswith("tr"))
        @self.subscription_service.require_subscription(1)
        def handle_call(call):
            self.handle_turkey(call)

    def handle_turkey(self, call):
        self.bot.answer_callback_query(call.id)
        data = call.data

        handler = self.routes.get(data)

        if handler:
            handler(call)


    def tr_menu(self, call):

        chat_id = call.message.chat.id
        self.clearstate(chat_id)

        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(InlineKeyboardButton("✏️Сделать расчет", style="success",callback_data="calc_tr"))
        keyboard.add(InlineKeyboardButton("📈Актуальный курс", callback_data="tr_currency_menu"))
        keyboard.add(InlineKeyboardButton("🎁Получить бесплатно eSim", callback_data="esim_tr"))
        button2 = InlineKeyboardButton("📋Меню", callback_data="main_menu")
        keyboard.add(button2)
        self.send_media(path="img/turkey.jpg", chat_id=chat_id,
                   caption='''🇹🇷<b>2Change — услуги в Турции\n\n🕒 График работы:</b>\nПн-Сб: 10:00 - 20:00 (Вс - выходной)\nОфис по записи''',
                   parse_mode="HTML", reply_markup=keyboard)

        return
    def tr_card_menu(self, call):
        chat_id = call.message.chat.id
        photo_path = "img/card_video.mp4"
        msg = (
            "💳 Друзья, есть возможность выпустить зарубежную карту <b>Bybit Card — доставим физическую карту</b> по России за 2 недели, а виртуальной можно оплачивать покупки в интернете уже через 10 минут! \n\n"
            ""
            "<b>Преимущества:</b> \n"
            "💰 Лимиты: до 5 000 $ в сутки и 50 000 $ в месяц.\n"
            "💳 Форматы: виртуальная и/или пластиковая карта.\n"
            "📦 Доставка в Россию — за 2 недели курьером прямо к двери.\n\n"
            ""
            "Санкции ужесточаются и оформить карту позже может стать сложнее.\n\n"
            ""
            "👉Напишите @ALEXANDRA_2CHANGE или оставьте заявку, чтобы узнать подробности")
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("Оставить заявку✅", callback_data="request/💳зарубежная карта/0"))
        keyboard.add(InlineKeyboardButton("Меню📋", callback_data="main_menu"))
        self.send_media(photo_path, chat_id, msg, keyboard, parse_mode="HTML")

        return

    def tr_other_menu(self, call):
        chat_id = call.message.chat.id
        msg = ("👋 <b>Добро пожаловать!</b>\n"
               "Здесь вы можете ознакомиться со всеми видами услуг сервиса <b>2Change</b>.\n\n"
               "<i>Мы помогаем с 💸 переводами, расчётами, оплатами и 📦 сопроводительными услугами для работы с разными странами 🌍 и платформами.</i>\n\n"
               "<b>👇 Нажмите, чтобы узнать подробности</b>")
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("Наличные через банкомат (QR-код)", callback_data="tr_qr_menu"))
        button1, button2 = InlineKeyboardButton("Перевод по IBAN",
                                                callback_data="tr_iban_menu"), InlineKeyboardButton(
            "Наличные в офисе", callback_data="tr_office_cash_menu")
        keyboard.row(button1, button2)
        keyboard.add(InlineKeyboardButton("Симкарта eSim📲", callback_data="tr_esim_menu"))
        keyboard.add(InlineKeyboardButton("Денежные переводы💸", callback_data="tr_cash_transactions_menu"))
        keyboard.add(InlineKeyboardButton("Открытие счета в турецком банке🇹🇷", callback_data="tr_acc"))
        keyboard.add(InlineKeyboardButton("Онлайн-сервисы и букинги💻", callback_data="tr_services_booking_menu"))
        keyboard.add(InlineKeyboardButton("Меню📋", callback_data="main_menu"))
        self.bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)
        return

    def tr_qr_menu(self, call):
        chat_id = call.message.chat.id
        msg = ("<b>💵 Как обменять РУБЛИ и USDT на наличные лиры за 5 минут?</b>\n\n"

               "Вы можете быстро и без карты получить наличные лиры в любом банкомате Турции!\n\n"

               "<b>👥 Кому подойдёт:</b>\n"
               "— Туристам и тем, у кого нет турецкой карты\n"
               "— Кто ценит сервис и поддержку на русском языке\n\n"

               "<b>🔄 Как это работает:</b>\n"
               "— Оставьте заявку в боте или напишите @ALEXANDRA_2CHANGE\n"
               "— Переведите рубли или USDT\n"
               "— Отправьте нам фото QR-кода на экране банкомата\n"
               "— Заберите наличные ₺\n\n"

               "<b>💰 Лимиты: от 5 000₺ до 100 000₺\n"
               "📶 Требование: телефон с интернетом</b>\n"
               "Бесплатно eSIM +1Гб можно оформить у менеджера — /manager\n"
               "<a href='https://telegra.ph/Nalichnye-cherez-QR-kod-v-bankomate-05-21'>📎 Подробнее и FAQ</a>\n\n"

               "<b>📊 Рассчитайте обмен или оставьте заявку 👇</b>"
               )
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✏️Сделать расчет", style="success",callback_data="calc"))
        keyboard.add(InlineKeyboardButton("👩‍💻 Позвать оператора", callback_data="request/🏧Выдача через банкомат по QR/1"))
        keyboard.add(InlineKeyboardButton("Меню📋", callback_data="main_menu"))
        self.send_media("img/turkey_qr.MP4", chat_id, msg, keyboard)
        return

    def tr_iban_menu(self, call):
        chat_id = call.message.chat.id
        msg = ("<b>💸 Обмен RUB или USDT → лиры на IBAN за 2 минуты!</b>\n\n"
               "<b>👤 Кому подойдёт:</b>\n"
               "— Владельцам карт турецких банков\n"
               "— Кто ценит скорость и удобство \n\n"
               ""
               "<b>🔄 Как это работает:</b>\n"
               "— Оставьте заявку в боте или напишите @ALEXANDRA_2CHANGE\n"
               "— Переведите рубли или USDT\n"
               "— Отправьте IBAN и ФИО (на английском)\n"
               "— Получите ₺ лиры на счёт\n\n"
               "💰 Лимиты: от 2 000₺ до 500 000₺\n"
               "<a href='https://telegra.ph/IBAN-05-21'>📎Подробнее и FAQ </a>\n\n"
               "👇 Рассчитайте обмен или задайте вопрос")
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✏️Сделать расчет",style="success", callback_data="calc"))
        keyboard.add(InlineKeyboardButton("👩‍💻 Позвать оператора", callback_data="request/🔄IBAN-перевод/1"))
        keyboard.add(InlineKeyboardButton("Меню📋", callback_data="main_menu"))
        self.send_media("img/tr_iban.jpg", chat_id, msg, keyboard)
        return
    def tr_office_cash_menu(self, call):
        chat_id = call.message.chat.id
        msg = ("<b>🏢 Получение наличных лир в офисе — Стамбул, Анталья, Аланья\n\n"
               ""
               "👥 Кому подойдёт:</b>\n"
               "— Кто хочет обменять крупную сумму\n"
               "— Кто предпочитает личную встречу\n\n"
               ""
               "<b>🔄 Как это работает:</b>\n"
               "— Приезжаете по записи\n"
               "— Переводите рубли\n"
               "— Получаете наличные лиры\n"
               "— Доллары или евро по запросу\n\n"
               "💰 Сумма: от 100 000₽\n"
               "<b>🕒 По записи минимум за 1 час</b>\n"
               "<a href='https://telegra.ph/Ofis-05-21-9'>📎 Подробнее и FAQ</a>\n\n"
               ""
               "<b>Рассчитайте обмен или оставьте заявку 👇</b>")
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✏️Сделать расчет",style="success", callback_data="calc"))
        keyboard.add(InlineKeyboardButton("👩‍💻 Позвать оператора", callback_data="request/💰Выдача наличных в офисе/1"))
        keyboard.add(InlineKeyboardButton("Меню📋", callback_data="main_menu"))
        self.bot.send_message(chat_id=chat_id, text=msg, reply_markup=keyboard, parse_mode="HTML")
        return
    def tr_cash_transactions_menu(self, call):
        chat_id = call.message.chat.id
        msg = ("Возможно получение на карту/счет, а также получение наличных.\n\n"
               "Доступны для перевода:\n"
               "🇪🇺 Европа\n🇦🇷 Аргентина\n🇧🇾 Беларусь\n🇧🇷 Бразилия\n🇬🇪 Грузия\n🇮🇳 Индия\n🇮🇩 Индонезия\n🇰🇿 Казахстан\n🇨🇦 Канада\n🇨🇳 Китай\n🇰🇷 Корея\n🇲🇽 Мексика\n🇦🇪 ОАЭ\n🇷🇺 Россия\n🇺🇸 США\n🇹🇭 Таиланд\n🇹🇷 Турция\n🇺🇿 Узбекистан и другие страны"
               "\nWise\nSepa\nRevolut\nAlipay/Wechat\nPaypal\n\n"
               ""
               "👇Оставьте заявку, и менеджер @ALEXANDRA_2CHANGE ответит на ваши вопросы")

        keyboard = InlineKeyboardMarkup()

        keyboard.add(InlineKeyboardButton("✅Узнать у менеджера", callback_data="request/💸Денежные переводы/0"))
        keyboard.add(InlineKeyboardButton("Меню📋", callback_data="main_menu"))
        self.bot.send_message(chat_id, msg, reply_markup=keyboard)
        return
    def tr_acc(self, call):
        chat_id = call.message.chat.id
        msg = ("<b>🏦 Оформление турецкой банковской карты — дистанционно</b>\n\n"
               ""
               "Без депозита. Без ВНЖ. Без визита в отделение.\n\n"
               ""
               "<b>📌 Доступные банки:\n• 🔵 DenizBank\n• 🟡 VakıfBank\n• 🟥 Ziraat Bankası</b>\n\n"
               ""
               "<b>Необходимые документы:</b>\n• 🛂 Загранпаспорт\n• 🧾 Турецкий ИНН (если нет — поможем оформить)\n\n"
               ""
               "👇Оставьте заявку, и менеджер @ALEXANDRA_2CHANGE ответит на ваши вопросы.")

        keyboard = InlineKeyboardMarkup()

        keyboard.add(InlineKeyboardButton("✅Узнать у менеджера", callback_data="request/Счет в банке 🇹🇷/1"))
        keyboard.add(InlineKeyboardButton("Меню📋", callback_data="main_menu"))
        self.bot.send_message(chat_id, msg, reply_markup=keyboard, parse_mode="HTML")
        return

    def tr_services_booking_menu(self, call):
        chat_id = call.message.chat.id
        msg = ("<b>💳 Оплата любых онлайн-сервисов за 3 минуты</b>\n\n"
               ""
               "Airbnb, Agoda, Booking, IKEA, PS Store, Netflix, визы, аренда авто и многое другое — оплачиваем быстро и без лишних шагов.\n\n💸"
               ""
               "<b>Условия:</b>\n"
               "• Оплата через наш аккаунт или ваш\n"
               "• Комиссия — фиксированная: 300 ₽\n"
               "• Оплата принимается в рублях (любой банк) и USDT\n\n"
               ""
               "<b>📌 Как это работает?</b>\n\n"
               "1. 🔗 Отправьте <a href='https://t.me/ALEXANDRA_2CHANGE'>👤 менеджеру</a> ссылку на сервис и нужные товары/услуги\n"
               "2. 📊 Получите расчёт в рублях\n"
               "3. 💵 Оплатите удобным способом\n"
               "4. ✅ Мы оплачиваем заказ или выдаём карту для самостоятельной оплаты (в зависимости от сервиса)\n\n"
               ""
               "<b>❓ Остались вопросы?</b>\n"
               "Оставьте заявку — всё расскажем и подскажем 👇")

        keyboard = InlineKeyboardMarkup()

        keyboard.add(
            InlineKeyboardButton("✅Узнать у менеджера", callback_data="request/Онлайн-сервисы  💻/1"))
        keyboard.add(InlineKeyboardButton("Меню📋", callback_data="main_menu"))
        self.bot.send_message(chat_id, msg, reply_markup=keyboard, parse_mode="HTML")
        return
    def tr_currency_menu(self, call):
        chat_id = call.message.chat.id# ТУРЦИЯ

        msg = self.finstr.show_currency(country=1)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✏️Рассчитать сумму",style="success", callback_data="calc_tr"))
        keyboard.add(InlineKeyboardButton("👩‍💻 Позвать оператора", callback_data="request/❔вопрос про курсы валют/1"))
        self.bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)
        return