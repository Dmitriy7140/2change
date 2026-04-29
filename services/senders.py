import time
from datetime import datetime

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import TEST_MODE, ADMIN_CHANNEL
from services.applications import ApplicationCreator

CHANNELS = {
    "turkey" : -1001606763790,
    "thailand" :-1003114769509,
    "china": -1003446339439,
    "korea" : -1001290060134,
    "vietnam":-1003683646201,


}


class SenderService:

    def __init__(self, bot, qdb, manager_chat_id, day_off_func, logger):
        self.logger = logger
        self.bot = bot
        self.qdb = qdb
        self.manager_chat_id = manager_chat_id
        self.day_off = day_off_func
        self.img_cache = {}

    def send_media(self,
                   path,
                   chat_id,
                   caption=None,
                   reply_markup=None,
                   parse_mode="HTML"):
        if path in self.img_cache:
            file_id = self.img_cache[path]
            if path.lower().endswith('.gif'):
                self.bot.send_animation(chat_id, file_id, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
            elif path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                self.bot.send_photo(chat_id, file_id, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
            else:  # mp4, avi и т.д.
                self.bot.send_video(chat_id, file_id, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
        else:
            with open(path, "rb") as media:
                if path.lower().endswith('.gif'):
                    sent = self.bot.send_animation(chat_id, media, caption=caption, reply_markup=reply_markup,
                                              parse_mode=parse_mode)
                    self.img_cache[path] = sent.animation.file_id
                elif path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    sent = self.bot.send_photo(chat_id, media, caption=caption, reply_markup=reply_markup,
                                          parse_mode=parse_mode)
                    self.img_cache[path] = sent.photo[-1].file_id
                else:  # видео
                    sent = self.bot.send_video(chat_id, media, caption=caption, reply_markup=reply_markup,
                                          parse_mode=parse_mode)
                    self.img_cache[path] = sent.video.file_id

    def send_application(self, user_id, user_name, chat_id, user_ref, reason=None, country=None, amount1=None, amount2=None,
                         currency1=None, currency2=None):
        msg = (
            "⚡️Ваша заявка уже в работе, скоро менеджер Александра с вами свяжется, ожидайте или напишите нам @alexandra_2change\n\n"
            "<b>🕰Наш график работы:</b>\n"
            "ПН-СБ: 10:00 - 20:00 (ВС выходной)"
            )
        if self.day_off():
            self.qdb.add_to_queue(country=country,
                                  tg_id=user_id,
                                  name=user_name,
                                  reason=reason,
                                  amount1=amount1,
                                  amount2=amount2,
                                  currency1=currency1,
                                  currency2=currency2)
            self.bot.send_message(chat_id, msg, parse_mode="HTML")

        else:
            keybord = InlineKeyboardMarkup()
            keybord.add(InlineKeyboardButton("💬Связаться с клиентом", callback_data="contact_client", style="success"))
            apmake = ApplicationCreator(country=country, client_name=user_name, reason=reason, amount1=amount1,
                                        amount2=amount2, currency1=currency1, currency2=currency2)

            msg_admin = apmake.create()
            sent_msg = self.bot.send_message(self.manager_chat_id, msg_admin, parse_mode="HTML", reply_markup=keybord)

            if self.qdb.set_user_name(sent_msg.message_id, user_id, user_ref):

                self.bot.send_message(chat_id, msg, parse_mode="HTML")
            else:
                self.bot.send_message(chat_id, "⛔️Менеджер не сможет вам написать из-за ваших настроек приватности⛔️\n "
                                          "Включите видимость вашего аккаунта по ссылке в настройках приватности, или напишите @ALEXANDRA_2CHANGE",
                                 parse_mode="HTML")

    def send_indev(self, chat_id):
        msg = ("<b>⚠️Мы пока дорабатываем эту функцию⚠️</b>\n\n"
               ""
               "💛Приносим свои извинения за неудобства, стараемся сделать ваш опыт использования бота комфортнее и лучше💛\n\n"
               ""
               "🔔Но наш менеджер всегда на связи, чтобы его позвать нажмите /manager")
        self.send_media("img/401.mp4", chat_id, caption=msg)

    def _form_daily_messages(self):
        r = self.qdb.get_currencies()
        title = (f"<b>Актуальный курс на {datetime.now().strftime("%d.%m")}</b>\n\n"
                 f""
                 f"<b>Вы отдаете<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Вы получаете</b>\n")

        msg_turkey =(f"{title}"
                     f"▪️Рубль<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Лира нал QR/офис {r["cash_rub_try"]:.2f}₽\n"
                     f"▪️Рубль<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Лира безнал IBAN {r["rub_try"]:.2f}₽\n"
                     f"▪️Лира<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Рубль {r["try_rub"]:.2f}₽\n"
                     f"▪️USDT<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Лира {r["usd_try"]:.2f}₺\n"
                     "▪️USDT<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Рубль и обратно по запросу\n"
                     "▪️Рубль<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Другие валюты по запросу\n\n"
                     ""
                     "<tg-emoji emoji-id='5370638904640676079'>➡️</tg-emoji><b>Акция!</b> Индивидуальный курс от 100 000₽\n"
                     "<tg-emoji emoji-id='5370638904640676079'>➡️</tg-emoji><b>Акция!</b> Бесплатная симкарта на 1ГБ всем подписчикам. А при обмене от 20 000 лир через QR - eSIM на 10ГБ в подарок!\n"
                     "⚜️<a href='https://t.me/turkey_2change/31568'>Подробные условия</a>\n\n"
                     ""
                     "<tg-emoji emoji-id='5471978009449731768'></tg-emoji>Пишите <a href='https://t.me/ALEXANDRA_2CHANGE'>\"ОБМЕН\"</a> @alexandra_2change либо оставьте заявку в <a href='https://t.me/official_2changebot'>боте</a>")
        msg_thailand = (f"{title}"
                     f"▪️Рубль<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Бат нал {r["cash_rub_thb"]:.2f}₽ (QR банкомат)\n"
                     f"▪️Рубль<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Бат безнал {r["rub_thb"]:.2f}₽\n"                     
                     f"▪️USDT<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Бат {r["usd_thb"]:.2f}฿\n"
                     "▪️USDT<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Рубль €$ бат и обратно по запросу\n"
                     "▪️Рубль<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Другие валюты по запросу\n\n"
                     ""
                     "<tg-emoji emoji-id='5370638904640676079'></tg-emoji><b>Акция!</b> Индивидуальный курс от 100 000₽\n"
                     "<tg-emoji emoji-id='5370638904640676079'></tg-emoji><b>Акция!</b> Бесплатная симкарта при обмене от 20 000 бат через QR - eSIM на 3ГБ в подарок!\n"
                     "⚜️<a href='https://t.me/thailand_2change/471'>Подробные условия</a>\n\n"
                     ""
                     "<tg-emoji emoji-id='5471978009449731768'></tg-emoji>Пишите <a href='https://t.me/ALEXANDRA_2CHANGE'>\"ОБМЕН\"</a> @alexandra_2change либо оставьте заявку в <a href='https://t.me/official_2changebot'>боте</a>")

        msg_china = (f"{title}"
                     f"▪️Рубль<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Юань {r["rub_cny"]:.2f} ₽ (AliPay/WeChat)\n"
                     f"▪️USDT<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Юань {r["usd_cny"]:.2f}  ¥\n"
                     f"▪️Юань<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Рубль {r["cny_rub"]:.2f} ₽\n"                     
                     "▪️Рубль<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Другие валюты по запросу\n\n"
                     "<tg-emoji emoji-id='5471978009449731768'></tg-emoji>Пишите <a href='https://t.me/ALEXANDRA_2CHANGE'>\"ОБМЕН\"</a> @alexandra_2change либо оставьте заявку в <a href='https://t.me/official_2changebot'>боте</a>\n\n"
                     ""
                     "<tg-emoji emoji-id='5370638904640676079'></tg-emoji><b>Акция!</b> Индивидуальный курс от 100 000₽\n"                    
                     "⚜️<a href='https://t.me/china_2change/10'>Подробные условия</a>\n\n"
                     ""
                     )

        msg_korea = (f"{title}"
                     f"▪️Рубль<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Воны: {r["rub_krw"]:.2f}₩\n"
                     f"▪️USDT<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Воны: {r["usd_krw"]:.2f}₩\n"
                     f"▪️Воны<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Рубли: {r["krw_rub"]:.2f}₩\n"
                     f"▪️Воны<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>USDT: {r["krw_usd"]:.2f}₩\n\n"
                     ""
                     "<tg-emoji emoji-id='5370638904640676079'></tg-emoji><b>Акция!</b> При обмене от <b>1 000 000₩</b> - симкарта <b>eSIM</b> в подарок!"
                     "<i><b>Оставьте заявку в <a href='https://t.me/official_2changebot'>боте</a></b></i>👈")

        msg_vietnam = (f"{title}"
                     f"▪️Рубль<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Донги нал {r["rub_vnd"]:.0f} VND\n"
                     f"▪️Рубль<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Донги безнал {r["cash_rub_vnd"]:.0f} VND\n"
                     f"▪️USDT<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Донги {r["usd_vnd"]:.0f} VND\n"
                     f"▪️Рубли<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>USDT Bybit Pay по запросу\n"
                     "▪️USDT<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Рубль, €$ и обратно по запросу\n"
                     "▪️Рубль<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Другие валюты по запросу\n\n"
                     ""
                     "<tg-emoji emoji-id='5370638904640676079'></tg-emoji><b>Акция!</b> Индивидуальный курс от 100 000₽\n"
                     "<tg-emoji emoji-id='5370638904640676079'></tg-emoji><b>Акция!</b> Бесплатная симкарта при обмене от 20 млн донгов через QR - eSIM на 10ГБ в подарок!\n"
                     "⚜️<a href='https://t.me/vietnam_2change/210'>Подробные условия</a>\n\n"
                     ""
                     "<tg-emoji emoji-id='5471978009449731768'></tg-emoji>Пишите <a href='https://t.me/ALEXANDRA_2CHANGE'>\"ОБМЕН\"</a> @alexandra_2change либо оставьте заявку в <a href='https://t.me/official_2changebot'>боте</a>")
        return {
            "turkey" : msg_turkey,
            "thailand": msg_thailand,
            "china": msg_china,
            "korea": msg_korea,
            "vietnam" : msg_vietnam,
        }


    def send_channel_notification(self):
        messages_dict = self._form_daily_messages()
        errors = {
        }
        for country, message in messages_dict.items():
            try:
                self.bot.send_message(text=message,chat_id=CHANNELS[country] if not TEST_MODE else ADMIN_CHANNEL, parse_mode="HTML")
                time.sleep(0.04)
            except Exception as e:
                errors[country] = e
                self.logger.error(f"Ошибка при рассылке дейликов в {country}: {e}")

        if errors:
            msg = ("При ежедневной рассылке возникли проблемы:\n"
                   f"<code>{errors}</code>")
        else:
            msg = f"<b>{'[ТЕСТ]' if TEST_MODE else "🤖:"}</b> Отправили курсы во все каналы, проблем не возникло🥝!"
        self.bot.send_message(text=msg, chat_id=ADMIN_CHANNEL, parse_mode="HTML")
