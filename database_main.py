import coinoxr
import datetime
import sqlite3
from contextlib import contextmanager
from utils import logger




class QueueDB:
    def __init__(self, path_to_db="database.db"):
        logger.info("Запускаем базу данных...")
        self.db_path = path_to_db
        self._init_db()

    def _init_db(self):
        with self.get_connection() as conn:
            c = conn.cursor()

            # Таблица queue
            c.execute('''CREATE TABLE IF NOT EXISTS queue (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tg_id INTEGER UNIQUE,
                        country INTEGER,
                        name TEXT,
                        amount INTEGER,
                        currency1 TEXT,
                        currency2 TEXT,
                        reason TEXT,
                        created_at TEXT)''')  # ✅ Убрана запятая
            logger.info("Таблица queue загружена...")
            # Таблица currency (отдельно)
            c.execute('''CREATE TABLE IF NOT EXISTS currency (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usd_rub REAL,    
                usd_thb REAL,
                usd_try REAL,
                try_rub REAL, 
                
                thb_rub REAL,
                thb_try REAL,
                updated_at TEXT)''')
            logger.info("Таблица с курсами загружена...")


            conn.commit()
            logger.info("Создали БД! Ну, или проверили что она на месте!")

    @contextmanager
    def get_connection(self):

        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        logger.info("Подключились к БД...")
        try:
            logger.info("Работаем в БД...")
            yield conn
        finally:
            logger.info("Закрыли БД...")
            conn.close()

    def add_to_queue(self,  tg_id, name, country=1,reason=None, amount=None, currency1=None,
                     currency2=None, time=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")):
        with self.get_connection() as conn:
            c = conn.cursor()  # ✅ Исправлено
            c.execute('SELECT 1 FROM queue WHERE tg_id = ?', (tg_id,))
            if c.fetchone():
                logger.warning(f"Игнорировано: tg_id={tg_id} уже существует!")
                return False

            if reason:
                c.execute('INSERT INTO queue (country, tg_id, name, reason, created_at) VALUES (?, ?, ?, ?, ?)',
                          (country, tg_id, name, reason, time))
                logger.info("В очередь добавлена заявка общего характера!")
            elif amount:
                if currency1 and currency2:
                    c.execute(
                        'INSERT INTO queue (country,tg_id, name, amount, currency1, currency2, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (country, tg_id, name, amount, currency1, currency2, time))
                    logger.info("В очередь добавлена заявка на обмен, обе валюты известны!")
                elif currency1:
                    c.execute('INSERT INTO queue (country, tg_id, name, amount, currency1, created_at) VALUES (?,?, ?, ?, ?, ?)',
                              (country, tg_id, name, amount, currency1, time))
                    logger.info("В очередь добавлена заявка на обмен, известна только первая валюта!")
                elif currency2:
                    c.execute('INSERT INTO queue (country, tg_id, name, amount, currency2, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                              (country,tg_id, name, amount, currency2, time))
                    logger.info("В очередь добавлена заявка на обмен, известна только вторая валюта!")
                else:
                    c.execute('INSERT INTO queue (country, tg_id, name, amount, created_at) VALUES (?, ?, ?, ?, ?)',
                              (country,tg_id, name, amount, time))
                    logger.info("В очередь добавлена заявка на обмен, известна только сумма!")
            else:
                logger.info("Что-то пошло не так при добавлении валюты!!!")
                return False

            conn.commit()
            logger.info("Коммит!")
            logger.info(f"{name} (ID {tg_id}) добавлен в очередь.")
            return True

    def get_from_queue(self):
        """Берёт последнюю запись из очереди, удаляет её в БД и возвращает как кортеж.
            Если записей нет — возвращает None.
            """
        with self.get_connection() as conn:
            c = conn.cursor()
            logger.info("Подтягиваем последнюю запись из очереди...")
            # 1. Берём последнюю запись
            c.execute("SELECT * FROM queue ORDER BY id DESC LIMIT 1")
            row = c.fetchone()
            logger.info("Подтянули!")

            if row is None:
                logger.info("Записей не осталось!")
                return None

            # row = (id, tg_id, country, name, amount, currency1, currency2, reason, created_at)

            last_id = row[0]

            # 2. Удаляем именно её
            c.execute("DELETE FROM queue WHERE id = ?", (last_id,))
            logger.info("Удалили запись из очереди...")

            conn.commit()
            logger.info("Коммит!")
            logger.info(f"Извлечена и удалена запись с id={last_id}!")

            return row  # кортеж со всеми полями, None сохраняются как есть

    def count_rows(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            logger.info("Считаем очередь...")
            c.execute("SELECT COUNT(*) FROM queue")
            count = c.fetchone()[0]
            logger.info(f"Посчитали, что осталось {count} заявок!")
        return count

    def update_currency(self):
        try:
            coinoxr.app_id = "159d37183d104e2cb66f4ca45a9cadb4"
            logger.info("Подсосались к апи...")

            all_courses = coinoxr.Latest().get(base=f"USD", show_alternative=True)
            usd_try = all_courses.body["rates"]["TRY"]
            usd_rub = all_courses.body["rates"]["RUB"]
            usd_thb = all_courses.body["rates"]["THB"]
            logger.info("Подтянули доллар (usd/try, usd/rub, usd/thb)...")
            all_courses = coinoxr.Latest().get(base=f"TRY", show_alternative=True)
            try_rub = all_courses.body["rates"]["RUB"]
            logger.info("Подтянули лиры (try/rub)...")
            all_courses = coinoxr.Latest().get(base=f"THB", show_alternative=True)
            thb_rub = all_courses.body["rates"]["RUB"]
            thb_try=all_courses.body["rates"]["TRY"]
            logger.info("Подтянули баты (thb/rub, thb/try)!")


        except Exception as e:
            logger.error(f"Ошибка с добавлением курса:{e}!!!")
            return None
        self.set_currency(usd_rub, usd_try, usd_thb, try_rub,thb_rub, thb_try)
        return True

    def set_currency(self, usd_rub, usd_try, usd_thb, try_rub, thb_rub, thb_try, time=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")):
        with self.get_connection() as conn:
            c = conn.cursor()
            logger.info("Вставляем курсы в таблицу...")
            c.execute('''INSERT INTO currency (usd_rub, usd_try, usd_thb, try_rub, thb_rub, thb_try, updated_at) VALUES (?,?,?,?,?, ?, ?)''', (usd_rub, usd_try, usd_thb, try_rub, thb_rub, thb_try, time))
            logger.info("Вставили!")
            conn.commit()
            logger.info("Коммит!")

    def get_currencies(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            logger.info("Подтягиваем курсы из таблицы...")
            c.execute("SELECT * FROM currency ORDER BY id DESC LIMIT 1")

            row = c.fetchone()
            logger.info("Подтянули курсы, даем!")
            return row


if __name__ == "__main__":
    qdb = QueueDB()
    qdb.update_currency()
    raw=qdb.get_currencies()
    print(raw)




