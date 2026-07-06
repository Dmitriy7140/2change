"""Кнопка-переход в мини-апп (Telegram Web App).

web_app-кнопка открывает ссылку именно как приложение во встроенном браузере
Telegram (работает в личных чатах). URL — в config.WEBAPP_URL.
"""
from telebot.types import InlineKeyboardButton, WebAppInfo

from config import WEBAPP_URL


def calc_button(text="✏️Сделать расчет"):
    return InlineKeyboardButton(text, web_app=WebAppInfo(url=WEBAPP_URL), style="success")
