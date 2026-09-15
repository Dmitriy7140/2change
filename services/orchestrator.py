import threading
import time


class CurrencyOrchestrator:
    def __init__(self, qdb,interest_service, logger):
        self.qdb = qdb
        self.interest_service = interest_service
        self.logger = logger
        self.interval = 20 * 60

        self._stop_flag = False
        self.thread = None

    def start(self):
        """Запуск фонового обновления"""
        if self.thread and self.thread.is_alive():
            self.logger.warning("CurrencyOrchestrator уже запущен")
            return

        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

        self.logger.info("CurrencyOrchestrator запущен")

    def stop(self):
        """Остановка (если понадобится)"""
        self._stop_flag = True
        self.logger.info("CurrencyOrchestrator остановлен")

    def _loop(self):
        while not self._stop_flag:
            try:
                self.logger.info("Обновляем наценки и курсы...")

                # Сначала читаем наценки: update_currency использует их из БД.
                if not self.interest_service.sync_interest():
                    self.logger.error("Не удалось загрузить наценки; фоновое обновление пропущено")
                elif self.interest_service.insert_currencies_into_table():
                    self.logger.info("Наценки и курсы обновлены в БД и Google-таблице")
                else:
                    self.logger.error("Фоновое обновление курсов завершилось с ошибкой")

            except Exception:
                self.logger.exception("Ошибка обновления наценок и курсов")

            # Повторяем обновление через 20 минут, в том числе после ошибки.
            time.sleep(self.interval)
