
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Callable




class EsimHandlers:

    def __init__(self, bot, subscription_service, sender_service, state_manager):
        self.bot = bot
        self.subscription_service = subscription_service
        self.sender_service = sender_service

        self.to_edit = {}
        self.img_cache = {}
        self.esim_countries = {
            "1": "esim_tr",
            "3": "esim_thai",
            "4": "esim_cn",
            "5": "esim_kr",
            "6": "esim_ae",
        }
        self.country_by_callback = {
            "esim_tr": 1,
            "esim_thai": 3,
            "esim_cn": 4,
            "esim_kr": 5,
            "esim_ae": 6,
        }
        self.routes : dict[str, Callable] = {
            "esim_main": self.esim_main,
            "esim_tr": self.esim_tr,
            "esim_thai": self.esim_thai,
            "esim_cn": self.esim_cn,
            "esim_kr": self.esim_kr,
            "esim_ae": self.esim_ae,
        }
        self.clearstate = state_manager.clear
    def register(self):
        @self.bot.callback_query_handler(func=lambda c: c.data.startswith("esim"))
        def handle(call):
            self.handle_esim(call)

    def handle_esim(self, call):
        self.bot.answer_callback_query(call.id)
        data = call.data

        # FAQ отдельно
        if data.startswith("esim_faq/"):
            return self.esim_faq(call)

        handler = self.routes.get(data)
        if not handler:
            return

        # Проверяем, нужна ли подписка
        country = self.country_by_callback.get(data)

        if country:
            user_id = call.from_user.id

            if not self.subscription_service.check_subscription(user_id, country):
                return self._send_subscription_required(call, country)

        handler(call)

    def _send_subscription_required(self, call, country):
        chat_id = call.message.chat.id
        chat_username = self.subscription_service.SUBSCRIPTION_CHATS.get(country)

        if not chat_username:
            return

        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton(
                "📢 Подписаться",
                url=f"https://t.me/{chat_username.replace('@', '')}"
            )
        )
        keyboard.add(
            InlineKeyboardButton(
                "🔄 Проверить снова",
                callback_data=call.data
            )
        )

        self.bot.send_message(
            chat_id,
            "❗ Для продолжения необходимо подписаться на канал.",
            reply_markup=keyboard
        )
    def _send_or_edit(self, call, msg, keyboard):
        chat_id = call.message.chat.id
        image_path = "img/esimmain.jpg"

        if chat_id in self.to_edit:
            self.bot.edit_message_caption(
                caption=msg,
                chat_id=chat_id,
                message_id=self.to_edit[chat_id],
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            return

        message = None  # ← добавили

        if image_path in self.img_cache:
            message = self.bot.send_photo(
                chat_id,
                photo=self.img_cache[image_path],
                caption=msg,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            with open(image_path, "rb") as media:
                message = self.bot.send_photo(
                    chat_id,
                    media,
                    caption=msg,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                self.img_cache[image_path] = message.photo[-1].file_id

        self.to_edit[chat_id] = message.message_id

    def esim_main(self, call):
        chat_id = call.message.chat.id
        self.clearstate(chat_id)
        if chat_id in self.to_edit:
            del self.to_edit[chat_id]
        msg = ("<b>Боитесь остаться без связи в чужой стране?</b>\n"
               "Роуминг дорогой, а местные симки — сплошная суета?\n"
               "<i>📲 Подключите eSIM с интернетом еще до вылета — быстро, удобно и с поддержкой на каждом шаге!</i>\n\n"
               ""
               "💡 Условия:\n"
               "✔️ Быстрое подключение\n"
               "✔️ Интернет <b><i>без визита в салон</i></b>\n"
               "✔️ Для каждой страны свои тарифы\n\n"
               ""
               "<b>📌 Часто задаваемые вопросы:</b>\n\n"
               "• Что такое eSIM? \n"
               "Электронная симкарта, встроенная в большинство современных смартфонов.\n\n"
               ""
               "• Как подключить eSIM?\n"
               "Сканируете QR-код → eSIM подключается → перед вылетом или уже по прилету в страну включаете eSIM и пользуетесь интерентом.\n\n"
               ""
               "<b>• Совместимость</b>\n"
               "— <b>iPhone:</b> Настройки → Сотовая связь → «Добавить eSIM»\n"
               "— <b>Android:</b> Настройки → Подключения / Сеть и интернет → Диспетчер SIM-карт → «Добавить eSIM»\n\n"
               "<i>👇 Выберите страну или напишите менеджеру @ALEXANDRA_2CHANGE 👩🏻‍💼</i>")
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("🇹🇷Турция", callback_data="esim_tr"),
                     InlineKeyboardButton("🇹🇭Тайланд", callback_data="esim_thai"))
        keyboard.row(InlineKeyboardButton("🇨🇳Китай", callback_data="esim_cn"),
                     InlineKeyboardButton("🇰🇷Корея", callback_data="esim_kr"))
        keyboard.add(InlineKeyboardButton("🇦🇪ОАЭ (Дубай)", callback_data="esim_ae"))
        keyboard.add(InlineKeyboardButton("📋Главное меню", callback_data="main_menu"))
        self.sender_service.send_media("img/esimmain.jpg", chat_id, msg, reply_markup=keyboard)
    def esim_tr(self, call):


        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("←", callback_data="esim_faq/1"),
            InlineKeyboardButton("1/2", callback_data="ignore"),
            InlineKeyboardButton("→", callback_data="esim_faq/1")
        )

        keyboard.add(
            InlineKeyboardButton(
                "Оставить заявку на eSIM✅",
                callback_data="request/📲получить eSIM/1"
            )
        )

        keyboard.add(
            InlineKeyboardButton("Другие страны🌏", callback_data="esim_main")
        )

        msg = (
            "🎁 <b>Дарим электронную симкарту eSIM</b> — без условий и скрытых платежей!\n\n"
            "Хотите оставаться на связи в Турции без переплат?\n"
            "Ловите подарок — eSIM с интернетом <b>абсолютно бесплатно!</b>\n\n"

            "<b>📱 Что такое eSIM?</b>\n"
            "Это интернет за границей без физической sim-карты.\n\n"

            "💡 <b>Что вы получите?</b>\n"
            "✔️ Бесплатное подключение\n"
            "✔️ 1 ГБ интернета\n"
            "✔️ Выгодное пополнение при необходимости\n\n"

            "🇹🇷 <b>5 ГБ — 1900₽</b>\n"
            "🇹🇷 <b>10 ГБ — 2500₽</b>\n"
            "🇹🇷 <b>20 ГБ — 3300₽</b>\n\n"

            "🎁 <b>Бонус +10 ГБ трафика в подарок</b>, "
            "при обмене от 20 000 лир через QR!\n\n"

            "👇 <b>Оставьте заявку</b> или напишите менеджеру\n"
            "@ALEXANDRA_2CHANGE 👩🏻‍💼"
        )

        self._send_or_edit(call, msg, keyboard)
    def esim_thai(self, call):
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("←", callback_data="esim_faq/3"),
            InlineKeyboardButton("1/2", callback_data="ignore"),
            InlineKeyboardButton("→", callback_data="esim_faq/3")
        )

        keyboard.add(
            InlineKeyboardButton(
                "Оставить заявку на eSIM✅",
                callback_data="request/📲получить eSIM/3"
            )
        )

        keyboard.add(
            InlineKeyboardButton("Другие страны🌏", callback_data="esim_main")
        )

        msg = (
            "<b>📲Хотите оставаться на связи в Тайланде?</b>\n"
            "<i>Подключите eSIM с интернетом еще до вылета — быстро, удобно и с поддержкой на каждом шагу!</i>\n\n"

            "<b>💡Что вы получите?</b>\n"
            "✔️ Бесплатное подключение\n"
            "✔️ Интернет на 30 дней\n"
            "✔️ Связь сразу по прилете — <b>без визита в салон</b>\n\n"

            "<b>💰Тарифы на 30 дней:</b>\n"
            "🇹🇭 1 ГБ — 400₽\n"
            "🇹🇭 3 ГБ — 800₽\n"
            "🇹🇭 5 ГБ — 1 100₽\n"
            "🇹🇭 10 ГБ — 1 800₽\n\n"

            "<b>Оставьте заявку или напишите менеджеру @ALEXANDRA_2CHANGE</b> 👩🏻‍💼"
        )

        self._send_or_edit(call, msg, keyboard)
    def esim_cn(self, call):
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("←", callback_data="esim_faq/4"),
            InlineKeyboardButton("1/2", callback_data="ignore"),
            InlineKeyboardButton("→", callback_data="esim_faq/4")
        )

        keyboard.add(
            InlineKeyboardButton(
                "Оставить заявку на eSIM✅",
                callback_data="request/📲получить eSIM/4"
            )
        )

        keyboard.add(
            InlineKeyboardButton("Другие страны🌏", callback_data="esim_main")
        )

        msg = (
            "<b>📲Хотите оставаться на связи в Китае?</b>\n"
            "<i>Подключите eSIM с интернетом еще до вылета — быстро, удобно и с поддержкой на каждом шагу!</i>\n\n"

            "<b>💡Что вы получите?</b>\n"
            "✔️ Бесплатное подключение\n"
            "✔️ Интернет на 30 дней\n"
            "✔️ Связь сразу по прилете — <b>без визита в салон</b>\n"
            "✔️ Работают даже заблокированные приложения в Китае!\n\n"

            "<b>💰Тарифы на 30 дней:</b>\n"
            "🇨🇳 1 ГБ — 450₽\n"
            "🇨🇳 3 ГБ — 900₽\n"
            "🇨🇳 5 ГБ — 1 250₽\n"
            "🇨🇳 10 ГБ — 1 800₽\n\n"

            "<b>Оставьте заявку или напишите менеджеру @ALEXANDRA_2CHANGE</b> 👩🏻‍💼"
        )

        self._send_or_edit(call, msg, keyboard)

    def esim_kr(self, call):
        keyboard = InlineKeyboardMarkup()

        keyboard.row(
            InlineKeyboardButton("←", callback_data="esim_faq/5"),
            InlineKeyboardButton("1/2", callback_data="ignore"),
            InlineKeyboardButton("→", callback_data="esim_faq/5")
        )

        keyboard.add(
            InlineKeyboardButton(
                "Оставить заявку на eSIM✅",
                callback_data="request/📲получить eSIM/5"
            )
        )

        keyboard.add(
            InlineKeyboardButton("Другие страны🌏", callback_data="esim_main")
        )

        msg = (
            "<b>📲Хотите оставаться на связи в Корее?</b>\n"
            "<i>Подключите eSIM с интернетом еще до вылета — быстро, удобно и с поддержкой на каждом шагу!</i>\n\n"

            "<b>💡Что вы получите?</b>\n"
            "✔️ Бесплатное подключение\n"
            "✔️ Интернет на 30 дней\n"
            "✔️ Связь сразу по прилете — <i>без визита в салон</i>\n"
            "🎁 <i>При обмене от 2 000 000 ₩ — eSIM + 3 ГБ интернета в подарок!</i>\n\n"

            "<b>💰Тарифы на 30 дней:</b>\n"
            "🇰🇷 5 ГБ — 1 600₽\n"
            "🇰🇷 10 ГБ — 3 000₽\n"
            "🇰🇷 20 ГБ — 6 000₽\n"
            "🇰🇷 50 ГБ — 12 000₽\n"
            "<b>♾ Безлимитный интернет</b> — 14 000₽\n\n"

            "<b>Оставьте заявку или напишите менеджеру @ALEXANDRA_2CHANGE</b> 👩🏻‍💼"
        )

        self._send_or_edit(call, msg, keyboard)

    def esim_ae(self, call):
        keyboard = InlineKeyboardMarkup()

        keyboard.row(
            InlineKeyboardButton("←", callback_data="esim_faq/6"),
            InlineKeyboardButton("1/2", callback_data="ignore"),
            InlineKeyboardButton("→", callback_data="esim_faq/6")
        )

        keyboard.add(
            InlineKeyboardButton(
                "Оставить заявку на eSIM✅",
                callback_data="request/📲получить eSIM/6"
            )
        )

        keyboard.add(
            InlineKeyboardButton("Другие страны🌏", callback_data="esim_main")
        )

        msg = (
            "<b>📲Хотите оставаться на связи в ОАЭ?</b>\n"
            "<i>Подключите eSIM с интернетом еще до вылета — быстро, удобно и с поддержкой на каждом шагу!</i>\n\n"

            "<b>💡Что вы получите?</b>\n"
            "✔️ Бесплатное подключение\n"
            "✔️ Интернет на 30 дней\n"
            "✔️ Связь сразу по прилете — <b>без визита в салон</b>\n\n"

            "<b>💰Тарифы на 30 дней:</b>\n"
            "🇦🇪 1 ГБ — 1 300₽\n"
            "🇦🇪 3 ГБ — 3 500₽\n"
            "🇦🇪 5 ГБ — 5 000₽\n"
            "🇦🇪 10 ГБ — 8 500₽\n\n"

            "<b>Оставьте заявку или напишите менеджеру @ALEXANDRA_2CHANGE</b> 👩🏻‍💼"
        )

        self._send_or_edit(call, msg, keyboard)

    def esim_faq(self, call):

        _, country = call.data.split("/")

        target_callback = self.esim_countries.get(country)

        if not target_callback:
            return
        msg = ("Часто задаваемые вопросы:\n\n"
               ""
               "<b>• Что такое eSIM?</b>\n"
               "Это электронная симкарта, встроенная в современные смартфоны, большинство айфонов от 11 модели поддерживают eSIM.\n\n"
               ""
               "<b>• Как подключить eSIM?</b>\n"
               "Сканируйте QR-код - телефон активирует eSIM, интернет заработает.\n\n"
               ""
               "<b>• Совместимость</b>\n"
               "— <b>iPhone:</b> Настройки → Сотовая связь → «Добавить eSIM»\n"
               "— <b>Android:</b> Настройки → Подключения / Сеть и интернет → Диспетчер SIM-карт → «Добавить eSIM»\n\n"
               ""
               "<b>• Как это работает по шагам</b>\n"
               "Сканируете QR→ eSIM подключается → перед вылетом или уже в стране включаете и пользуетесь.\n\n"
               ""
               "<i>👇Оставьте заявку или напишите менеджеру @ALEXANDRA_2CHANGE🦸🏻‍♀️</i>")
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("←", callback_data=target_callback),
            InlineKeyboardButton("2/2", callback_data="ignore"),
            InlineKeyboardButton("→", callback_data=target_callback),
        )

        keyboard.add(
            InlineKeyboardButton(
                "Оставить заявку на eSIM✅",
                callback_data=f"request/📲получить eSIM/{country}"
            )
        )

        keyboard.add(
            InlineKeyboardButton("Другие страны🌏", callback_data="esim_main")
        )

        self._send_or_edit(call, msg, keyboard)