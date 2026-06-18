"""
Реестр deep-link'ов: callback_data меню -> функция, показывающая это меню.

Источник функций — словари `routes` у хендлеров стран/сервисов. По ссылке вида
    t.me/<bot>?start=<menu_key>__<источник>
бот первым сообщением открывает меню <menu_key> (а не главное меню).

Меню-функции принимают CallbackQuery, поэтому при старте подсовываем им
минимальный объект _FakeCall на основе сообщения /start.
"""


class _FakeCall:
    """Минимальный CallbackQuery-подобный объект для вызова меню при /start."""

    def __init__(self, message, data):
        self.message = message
        self.data = data
        self.from_user = message.from_user
        self.id = None


class DeepLinkRouter:
    def __init__(self, logger=None):
        self._routes = {}
        self.logger = logger

    def register(self, routes: dict):
        """Добавить маршруты хендлера (его self.routes)."""
        if routes:
            self._routes.update(routes)

    def has(self, menu_key: str) -> bool:
        return menu_key in self._routes

    def open(self, message, menu_key: str) -> bool:
        """Открыть меню по ключу. True — если меню найдено и показано."""
        handler = self._routes.get(menu_key)
        if self.logger:
            self.logger.info(
                f"deeplink open: key={menu_key!r} found={handler is not None} "
                f"registry_size={len(self._routes)}"
            )
        if not handler:
            return False
        try:
            handler(_FakeCall(message, menu_key))
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"deeplink open error ({menu_key}): {e}", exc_info=True)
            return False
