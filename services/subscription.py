from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiTelegramException
from functools import wraps


class SubscriptionService:
    SUBSCRIPTION_URLS = {
        1: "https://t.me/+XgJcXXDuPwAyODNi",
        2: "https://t.me/+kfAL5bXDpK41ODBh",
        3: "https://t.me/+Ys02t7bsEmRhZDYy",
        4: "https://t.me/+4w_OVP0LlO41NGEx",
        5: "https://t.me/+ZuxXbKKtlQRlZjgy",
        6: "https://t.me/+dBzBb6UlyiZiYjRh",
        7: "https://t.me/+vLNtACVKxo8xYmJh"
    }
    SUBSCRIPTION_CHATS = {
        1: "@turkey_2change",
        2: "@russia_2change",
        3: "@thailand_2change",
        4: "@china_2change",
        5: "@korea_obmen1",
        6: "@uae_2change",
        7: "@vietnam_2change"
    }

    def __init__(self, bot, logger, test_mode=False):
        self.bot = bot
        self.logger = logger
        self.test_mode = test_mode


    def check_subscription(self, user_id:int, country:int) -> bool:

        chat_username = self.SUBSCRIPTION_CHATS.get(country)
        if not chat_username:
            self.logger.error(f"Не найден чат для country={country}")
            return True
        if self.test_mode:
            return True
        try:
            chat_member = self.bot.get_chat_member(chat_username, user_id)
            self.logger.info("Пользователь")
            return chat_member.status in ("creator", "administrator", "member", "restricted")
        except ApiTelegramException as e:

            self.logger.error(f"Ошибка проверки подписки: {e}")
            return True

    def require_subscription(self, country: int):
        """country_names = {1: "🇹🇷Турция", 2: "🇷🇺Россия", 3: "🇹🇭Тайланд", 4: "🇨🇳Китай", 5: "Корея", 6 : ОАЭ, 7: вьетнам}"""
        def decorator(func):
            @wraps(func)
            def wrapper(call, *args, **kwargs):
                user_id = call.from_user.id
                chat_id = call.message.chat.id

                if not self.check_subscription(user_id, country):

                    keyboard = InlineKeyboardMarkup()
                    chat_url = self.SUBSCRIPTION_URLS[country]


                    keyboard.add(
                        InlineKeyboardButton(
                            "📢 Подписаться",
                            url=f"{chat_url}"
                        )
                    )
                    keyboard.add(
                        InlineKeyboardButton("🔄 Проверить снова", callback_data=call.data)
                    )

                    self.bot.send_message(
                        chat_id,
                        "❗ Для продолжения необходимо подписаться на канал.",
                        reply_markup=keyboard
                    )
                    return

                return func(call, *args, **kwargs)

            return wrapper
        return decorator