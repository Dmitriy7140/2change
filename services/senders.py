from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from services.applications import ApplicationCreator

class SenderService:

    def __init__(self, bot, qdb, manager_chat_id, day_off_func):
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
            keybord.add(InlineKeyboardButton("💬Связаться с клиентом", callback_data="contact_client"))
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