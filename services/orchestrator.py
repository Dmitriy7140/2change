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
                self.logger.info("Обновляем курсы...")

                # 1. обновили курсы через API внутри qdb


                # 2. записали в таблицу currency

                self.interest_service.insert_currencies_into_table()
                self.logger.info("Курсы обновлены и записаны в БД")



            except Exception as e:
                self.logger.error(f"Ошибка обновления курсов: {e}")

            # ждём 3 часа
            time.sleep(self.interval)