import time
from datetime import datetime

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import TEST_MODE, ADMIN_CHANNEL
from services.application_creator_service import ApplicationCreator

CHANNELS = {
    "turkey" : -1001606763790,
    "thailand" :-1003114769509,
    "china": -1003446339439,
    "korea" : -1001290060134,
    "vietnam":-1003683646201,


}
EMOJI = {
    'green_light':"<tg-emoji emoji-id='5267229058659264159'></tg-emoji>",
    'bl_arrow_right' : "<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>",
    'golden_tick' : "<tg-emoji emoji-id='5370638904640676079'></tg-emoji>",
    #compaines
    'apple': "<tg-emoji emoji-id='5318795767454923927'></tg-emoji>",
    'appstore': "<tg-emoji emoji-id='5366400016732666411'></tg-emoji>",
    'google_play':"<tg-emoji emoji-id='5366085865644768099'></tg-emoji>",
    'musically':"<tg-emoji emoji-id='5318890501548570977'></tg-emoji>",
    'netflix':"<tg-emoji emoji-id='5366477429223209600'></tg-emoji>",
    'playstation':"<tg-emoji emoji-id='5363934885893389858'></tg-emoji>",
    'xbox':"<tg-emoji emoji-id='5366104999724072406'></tg-emoji>",
    'steam':"<tg-emoji emoji-id='5318801707394695066'></tg-emoji>",
    'gpt':"<tg-emoji emoji-id='5310259124817134249'></tg-emoji>",
    'claude':"<tg-emoji emoji-id='5321196473784773037'></tg-emoji>",
    'photoshop':"<tg-emoji emoji-id='5352556692892564574'></tg-emoji>"
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
        title = (f"<b>{EMOJI['green_light']}Актуальный курс на {datetime.now().strftime("%d.%m")}</b>\n\n"
                 f""
                 f"<b>Вы отдаете{EMOJI['bl_arrow_right']}Вы получаете</b>\n")

        msg_turkey =(f"{title}"
                     f"▪️Рубли{EMOJI['bl_arrow_right']}Лиры нал <a href='https://t.me/turkey_2change/52581'>QR</a>/<a href='https://t.me/turkey_2change/56422'>офис</a> {r["cash_rub_try"]:.2f}₽\n"
                     f"▪️Рубли{EMOJI['bl_arrow_right']}Лиры безнал <a href='https://t.me/turkey_2change/52610'>IBAN</a> {r["rub_try"]:.2f}₽\n"
                     f"▪️Лиры{EMOJI['bl_arrow_right']}Рубли <a href='https://t.me/turkey_2change/58526'>нал/безнал</a> {r["try_rub"]:.2f}₽\n"
                     f"▪️USDT{EMOJI['bl_arrow_right']}Лиры {r["usd_try"]:.2f}₺\n"
                     f"▪️Рубли{EMOJI['bl_arrow_right']}USDT {r["rub_usd"]:.2f}₽\n"
                     f"▪️USDT{EMOJI['bl_arrow_right']}Рубли {r["usd_rub"]:.2f}₽\n"
                     f"▪️Рубли{EMOJI['bl_arrow_right']}Другие валюты по запросу\n"
                     f"▪️eSIM от 1300₽\n\n"
                     ""
                     f"<blockquote expandable>{EMOJI['golden_tick']}<b>Акция!</b> Индивидуальный курс от 100 000₽\n"
                     f"{EMOJI['golden_tick']}<b>Акция!</b> Бесплатная симкарта на 1ГБ всем подписчикам. А при обмене от 20 000 лир <a href='https://t.me/turkey_2change/52581'>через QR</a> - <a href='https://t.me/turkey_2change/58134'>eSIM</a>  на 10ГБ в подарок!\n"
                     f"{EMOJI['golden_tick']}<a href='https://t.me/turkey_2change/55039'>Оплата инвойсов (товары, обучение, лечение, недвижимость) - спец. курс!</a>\n"
                     f"{EMOJI['golden_tick']}<b>Помощь с <a href='https://2pay.money/?utm_source=tg&utm_content=kurs'>оплатой сервисов/игр!</a></b>{EMOJI['apple']}{EMOJI['appstore']}{EMOJI['google_play']}{EMOJI['musically']}{EMOJI['netflix']}{EMOJI['playstation']}{EMOJI['xbox']}{EMOJI['steam']}{EMOJI['gpt']}{EMOJI['claude']}{EMOJI['photoshop']} для россиян (смена региона iCloud+, турецкий аккаунт PlayStation/Xbox и многое другое на сайте!\n"
                     f"{EMOJI['golden_tick']}<b>Регистрация <a href='https://2change.pro/instrukcii/karty'>зарубежных карт</a> на загран паспорт РФ</b>"
                     f"</blockquote>\n\n"
                     ""
                     f"⚜️<a href='https://telegram.me/turkey_2change/56086'>Подробные условия</a>| <a href='https://t.me/review_2change'>Отзывы</a>|<a href='https://2change.pro/'>Сайт</a>\n\n"
                     "✅Пишите  <a href='https://t.me/m/hdlFzYyAMmIy'>«ОБМЕН» @alexandra_2change</a> либо оставьте заявку в <a href='https://t.me/official_2changebot'>боте-калькуляторе</a>")

        msg_thailand = (f"{title}"
                     f"▪️Рубли{EMOJI['bl_arrow_right']}Баты нал {r["cash_rub_thb"]:.2f}₽ (<a href='https://t.me/thailand_2change/4408'>QR банкомат</a>)\n"
                     f"▪️Рубли{EMOJI['bl_arrow_right']}Баты безнал {r["rub_thb"]:.2f}₽\n"                     
                     f"▪️USDT{EMOJI['bl_arrow_right']}Баты {r["usd_thb"]:.2f}฿\n"
                     f"▪️Рубли{EMOJI['bl_arrow_right']}USDT {r["rub_usd"]:.2f}₽\n"
                     f"▪️USDT{EMOJI['bl_arrow_right']}Рубли {r["usd_rub"]:.2f}₽\n"                     
                     f"▪️Рубли{EMOJI['bl_arrow_right']}Другие валюты по запросу\n"
                     " ▪️ eSIM от 400₽\n\n"
                     f"<blockquote expandable>{EMOJI['golden_tick']}<b>Акция!</b> Индивидуальный курс от 100 000₽\n"
                     f"{EMOJI['golden_tick']}<b>Акция!</b> Бесплатная симкарта при обмене от 20 000 бат через QR - eSIM на 3ГБ в подарок!\n"
                     f"{EMOJI['golden_tick']}<a href='https://t.me/thailand_2change/4411'>Оплата инвойсов (товары, недвижимость) - спец. курс!</a>\n"
                     f"{EMOJI['golden_tick']}<b>Помощь с <a href='https://2pay.money/?utm_source=tg&utm_content=kurs'>оплатой сервисов/игр!</a></b>{EMOJI['apple']}{EMOJI['appstore']}{EMOJI['google_play']}{EMOJI['musically']}{EMOJI['netflix']}{EMOJI['playstation']}{EMOJI['xbox']}{EMOJI['steam']}{EMOJI['gpt']}{EMOJI['claude']}{EMOJI['photoshop']} для россиян (смена региона iCloud+, турецкий аккаунт PlayStation/Xbox и многое другое на сайте!\n"
                     f"{EMOJI['golden_tick']}<b>Регистрация <a href='https://2change.pro/instrukcii/karty'>зарубежных карт</a> на загран паспорт РФ</b>"
                     f"</blockquote>\n\n"
                     ""
                     f"⚜️<a href='https://t.me/thailand_2change/4383'>Подробные условия</a>| <a href='https://t.me/review_2change'>Отзывы</a>|<a href='https://2change.pro/thailand'>Сайт</a>\n\n"
                     "✅Пишите  <a href='https://t.me/m/hdlFzYyAMmIy'>«ОБМЕН» @alexandra_2change</a> либо оставьте заявку в <a href='https://t.me/official_2changebot'>боте-калькуляторе</a>")

        msg_china = (f"{title}"
                     f"▪️Рубль<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Юань {r["rub_cny"]:.2f} ₽ (<a href='https://t.me/china_2change/2163'>AliPay/WeChat</a>)\n"
                     f"▪️USDT<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Юань {r["usd_cny"]:.2f}  ¥\n"
                     f"▪️Юань<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Рубль {r["cny_rub"]:.2f} ₽\n"
                     f"▪️Рубли<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>USDT {r["rub_usd"]:.2f}₽\n"
                     f"▪️USDT<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Рубли {r["usd_rub"]:.2f}₽\n"
                     "▪️Рубль<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Другие валюты по запросу\n\n"
                     ""
                     f"<blockquote expandable>{EMOJI['golden_tick']}<b>Акция!</b> Индивидуальный курс от 100 000₽\n"
                     f"{EMOJI['golden_tick']}<a href='https://t.me/china_2change/2768'>Регистрация Alipay/WeChat</a>  + <a href='https://t.me/china_2change/2766'>оформление eSIM</a>\n"
                     f"{EMOJI['golden_tick']}<a href='https://t.me/turkey_2change/55039'>Оплата инвойсов (товары, обучение, лечение, недвижимость) - спец. курс!</a>\n"
                     f"{EMOJI['golden_tick']}<b>Помощь с <a href='https://2pay.money/?utm_source=tg&utm_content=kurs'>оплатой сервисов/игр!</a></b>{EMOJI['apple']}{EMOJI['appstore']}{EMOJI['google_play']}{EMOJI['musically']}{EMOJI['netflix']}{EMOJI['playstation']}{EMOJI['xbox']}{EMOJI['steam']}{EMOJI['gpt']}{EMOJI['claude']}{EMOJI['photoshop']} для россиян (смена региона iCloud+, турецкий аккаунт PlayStation/Xbox и многое другое на сайте!\n"
                     f"{EMOJI['golden_tick']}<b>Регистрация <a href='https://2change.pro/instrukcii/karty'>зарубежных карт</a> на загран паспорт РФ</b>"
                     f"</blockquote>\n\n"
                     ""
                     f"⚜️<a href='https://telegram.me/china_2change/2129'>Подробные условия</a>| <a href='https://t.me/review_2change'>Отзывы</a>|<a href='https://2change.pro/china'>Сайт</a>\n\n"
                     "✅Пишите  <a href='https://t.me/m/hdlFzYyAMmIy'>«ОБМЕН» @alexandra_2change</a> либо оставьте заявку в <a href='https://t.me/official_2changebot'>боте-калькуляторе</a>")



        msg_korea = (f"{title}"
                     f"▪️Рубль{EMOJI['bl_arrow_right']}Воны: {r["rub_krw"]:.2f}₩\n"
                     f"▪️USDT{EMOJI['bl_arrow_right']}Воны: {r["usd_krw"]:.2f}₩\n"
                     f"▪️Воны{EMOJI['bl_arrow_right']}Рубли: {r["krw_rub"]:.2f}₩\n"
                     f"▪️Воны{EMOJI['bl_arrow_right']}USDT: {r["krw_usd"]:.2f}₩\n"
                     f"▪️Рубли{EMOJI['bl_arrow_right']}USDT {r["rub_usd"]:.2f}₽\n"
                     f"▪️USDT{EMOJI['bl_arrow_right']}Рубли {r["usd_rub"]:.2f}₽\n\n"
                     f"▪️eSIM от 1 600₽\n\n"
                     f""
                     f"<blockquote expandable>{EMOJI['golden_tick']}<b>Акция!</b> При обмене от <b>1 000 000₩</b> - <a href='https://t.me/korea_obmen1/7844'>симкарта <b>eSIM</b></a> в подарок!\n"
                     f"{EMOJI['golden_tick']}<b><a href='https://t.me/korea_obmen1/7841'>Оплата инвойсов</a></b> (товары, авто, <a href='https://t.me/korea_obmen1/7875'>обучение</a>, лечение) — спец. курс!\n\n"
                     f""
                     f"{EMOJI['golden_tick']}<b>Помощь с <a href='https://2pay.money/?utm_source=tg&utm_content=kurs'>оплатой сервисов/игр!</a></b>{EMOJI['apple']}{EMOJI['appstore']}{EMOJI['google_play']}{EMOJI['musically']}{EMOJI['netflix']}{EMOJI['playstation']}{EMOJI['xbox']}{EMOJI['steam']}{EMOJI['gpt']}{EMOJI['claude']}{EMOJI['photoshop']} для россиян (смена региона iCloud+, турецкий аккаунт PlayStation/Xbox и многое другое на сайте!\n"
                     f"{EMOJI['golden_tick']}<b>Регистрация <a href='https://2change.pro/instrukcii/karty'>зарубежных карт</a> на загран паспорт РФ</b>"
                     f"</blockquote>\n\n"
                     ""
                     f"⚜️<a href='https://t.me/korea_obmen1/7402'>Подробные условия</a>| <a href='https://t.me/review_2change'>Отзывы</a>|<a href='https://2change.pro/korea'>Сайт</a>\n\n"
                     "✅Пишите  <a href='https://t.me/m/hdlFzYyAMmIy'>«ОБМЕН» @alexandra_2change</a> либо оставьте заявку в <a href='https://t.me/official_2changebot'>боте-калькуляторе</a>")

        msg_vietnam = (f"{title}"
                     f"▪️Рубль<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Донги нал {r["rub_vnd"]:.0f} VND\n"
                     f"▪️Рубль<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Донги безнал {r["cash_rub_vnd"]:.0f} VND\n"
                     f"▪️USDT<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Донги {r["usd_vnd"]:.0f} VND\n"
                     f"▪️Донги<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Рубль {1/r["vnd_rub"]:.0f} VND\n"
                     f"▪️Рубли<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>USDT Bybit Pay {r["rub_usd"]:.2f}₽\n"
                     f"▪️USDT<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Рубли {r["usd_rub"]:.2f}₽\n"
                     "▪️USDT<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Рубль, €$ и обратно по запросу\n"
                     "▪️Рубль<tg-emoji emoji-id='5974140856939056410'>➡️</tg-emoji>Другие валюты по запросу\n\n"
                     ""
                     f"<blockquote expandable>{EMOJI['golden_tick']}<b>Акция!</b> Индивидуальный курс от 100 000₽\n"
                     f"{EMOJI['golden_tick']}<b>Акция!</b> Бесплатная eSIM на 10ГБ при обмене от 20 млн донгов через <a href='https://t.me/vietnam_2change/1998'>банкомат</a>!\n"
                     f"{EMOJI['golden_tick']}<b>Акция!</b> Бесплатно откроем вьетнамский счёт <a href='https://t.me/vietnam_2change/2031'>BybitPay</a> за 5 мин по РФ паспорту!\n"
                     f"{EMOJI['golden_tick']}<a href='https://t.me/vietnam_2change/1476'>Оплата инвойсов</a> (товары, недвижимость) - спец. курс!\n"
                     f"{EMOJI['golden_tick']}<b>Помощь с <a href='https://2pay.money/?utm_source=tg&utm_content=kurs'>оплатой сервисов/игр!</a></b>{EMOJI['apple']}{EMOJI['appstore']}{EMOJI['google_play']}{EMOJI['musically']}{EMOJI['netflix']}{EMOJI['playstation']}{EMOJI['xbox']}{EMOJI['steam']}{EMOJI['gpt']}{EMOJI['claude']}{EMOJI['photoshop']} для россиян (смена региона iCloud+, турецкий аккаунт PlayStation/Xbox и многое другое на сайте!\n"
                     f"{EMOJI['golden_tick']}<b>Регистрация <a href='https://2change.pro/instrukcii/karty'>зарубежных карт</a> на загран паспорт РФ</b>"
                     f"</blockquote>\n\n"
                     ""
                     f"⚜️<a href='https://telegram.me/vietnam_2change/1963'>Подробные условия</a>| <a href='https://t.me/review_2change'>Отзывы</a>|<a href='https://2change.pro/vietnam'>Сайт</a>\n\n"
                     "✅Пишите  <a href='https://t.me/m/hdlFzYyAMmIy'>«ОБМЕН» @alexandra_2change</a> либо оставьте заявку в <a href='https://t.me/official_2changebot'>боте-калькуляторе</a>")

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
