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
                        amount1 INTEGER,
                        amount2 REAL,
                        currency1 TEXT,
                        currency2 TEXT,
                        reason TEXT,
                        created_at TEXT)''')  # ✅ Убрана запятая
            logger.info("Таблица queue загружена...")
            # Таблица currency (отдельно)
            c.execute('''CREATE TABLE IF NOT EXISTS currency (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usd_rub REAL,
                rub_usd REAL,
                    
                
                usd_try REAL,
                cash_usd_try REAL,
                rub_try REAL,
                cash_rub_try REAL,
                try_rub REAL, 
                
                usd_thb REAL,
                cash_usd_thb REAL,
                rub_thb REAL,
                cash_rub_thb REAL,
                updated_at TEXT)''')
            logger.info("Таблица с курсами загружена...")
            # c.execute('''CREATE TABLE IF NOT EXISTS calc_states (
            #                 chat_id INTEGER PRIMARY KEY,
            #                 country INTEGER,
            #                 currency1 INTEGER,
            #                 currency2 INTEGER,
            #                 created_at TEXT)''')
            # logger.info("Таблица с состояниями загружена...")
            c.execute('''CREATE TABLE IF NOT EXISTS coef (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            usd_rub_c REAL, 
                            rub_usd_c REAL,
                            
                            usd_try_c REAL,
                            cash_usd_try_c REAL,
                            rub_try_c REAL,
                            cash_rub_try_c REAL,
                            try_rub_c REAL,
                            
                            usd_thb_c REAL,
                            cash_usd_thb_c REAL,
                            rub_thb_c REAL,
                            cash_rub_thb_c REAL,
                            updated_at TEXT)''')
            logger.info("Таблица с наценкой загружена...")
            c.execute("SELECT COUNT(*) FROM coef")
            count = c.fetchone()[0]

            if count == 0:  # Только если таблица пустая
                c.execute('''INSERT INTO coef (usd_rub_c, rub_usd_c, usd_try_c, cash_usd_try_c, rub_try_c, cash_rub_try_c, try_rub_c, usd_thb_c, cash_usd_thb_c, rub_thb_c, cash_rub_thb_c, updated_at) 
                                             VALUES (0.03,    0.03,         0.03, 0.05,     0.03,        0.05,         0.03,      0.03,        0.05,         0.03,      0.05,          ?)''', ("default",))

                logger.info("Начальные коэффициенты добавлены")
            else:
                logger.info(f"Таблица с наценкой уже содержит {count} записей, пропуск INSERT")


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

    def add_to_queue(self,  tg_id, name, country=1,reason=None, amount1=None, amount2=None, currency1=None,
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
            elif amount1:
                if currency1 and currency2:
                    c.execute(
                        'INSERT INTO queue (country,tg_id, name, amount, currency1, currency2, created_at) VALUES (?, ?, ?,?, ?, ?, ?, ?)',
                        (country, tg_id, name, amount1, amount2, currency1, currency2, time))
                    logger.info("В очередь добавлена заявка на обмен, обе валюты известны!")
                elif currency1:
                    c.execute('INSERT INTO queue (country, tg_id, name, amount, currency1, created_at) VALUES (?,?, ?,?, ?, ?, ?)',
                              (country, tg_id, name, amount1,amount2, currency1, time))
                    logger.info("В очередь добавлена заявка на обмен, известна только первая валюта!")
                elif currency2:
                    c.execute('INSERT INTO queue (country, tg_id, name, amount, currency2, created_at) VALUES (?,?, ?, ?, ?, ?, ?)',
                              (country,tg_id, name, amount1,amount2, currency2, time))
                    logger.info("В очередь добавлена заявка на обмен, известна только вторая валюта!")
                else:
                    c.execute('INSERT INTO queue (country, tg_id, name, amount, created_at) VALUES (?,?, ?, ?, ?, ?)',
                              (country,tg_id, name, amount1,amount2, time))
                    logger.info("В очередь добавлена заявка на обмен, известна только сумма!")
            else:
                logger.info("Что-то пошло не так при добавлении пользователя в очередь!!!")
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
            api_usd_try = all_courses.body["rates"]["TRY"]
            api_usd_rub = all_courses.body["rates"]["RUB"]
            api_usd_thb = all_courses.body["rates"]["THB"]
            logger.info("Подтянули доллар...")
            all_courses = coinoxr.Latest().get(base=f"TRY", show_alternative=True)
            api_try_rub = all_courses.body["rates"]["RUB"]
            logger.info("Подтянули лиры...")
            all_courses = coinoxr.Latest().get(base=f"THB", show_alternative=True)
            api_thb_rub = all_courses.body["rates"]["RUB"]

            logger.info("Подтянули баты!")

            rows_list= self.get_coef()
            rows = rows_list[0]

            api_courses= {"usd_try":api_usd_try,
                          "usd_rub":api_usd_rub,
                          "usd_thb":api_usd_thb,
                          "try_rub":api_try_rub,
                          "thb_rub":api_thb_rub}
            we_sell = {"id": rows[0],
                       "usd_rub_c": rows[1],
                       "rub_usd_c": rows[2],

                       "usd_try_c": rows[3],
                       "cash_usd_try_c":rows[4],
                       "rub_try_c": rows[5],
                       "cash_rub_try_c": rows[6],
                       "try_rub_c": rows[7],

                       "usd_thb_c": rows[8],
                       "cash_usd_thb_c": rows[9],
                       "rub_thb_c": rows[10],
                       "cash_rub_thb_c": rows[11],
                       }


            #РУБЛИ
            usd_rub= api_usd_rub -(api_usd_rub*we_sell["usd_rub_c"])
            rub_usd = api_usd_rub *(1+we_sell["rub_usd_c"])



            #ЛИРЫ
            usd_try = api_usd_try-(api_usd_try* we_sell["usd_try_c"])
            cash_usd_try = api_usd_try - (api_usd_try*we_sell["cash_usd_try_c"])
            rub_try = api_try_rub * (1 + we_sell["rub_try_c"])
            cash_rub_try = api_try_rub * (1 + we_sell["cash_rub_try_c"])
            try_rub=api_try_rub-(api_try_rub*we_sell["try_rub_c"]) #ЧЕЛ ДАЕТ ЛИРУ, ПОЛУЧАЕТ РУБЛЬ. НАША ВЫГОДА ОСТАВИТЬ БОЛЬШЕ РУБЛЕЙ

            #БАТЫ
            usd_thb = api_usd_thb - (api_usd_thb * +we_sell["usd_thb_c"])
            cash_usd_thb = api_usd_thb - (api_usd_thb * we_sell["cash_usd_thb_c"])
            rub_thb= api_thb_rub *(1 + we_sell["rub_thb_c"])
            cash_rub_thb= api_thb_rub *(1 + we_sell["cash_rub_thb_c"])

            rates = (usd_rub,rub_usd,usd_try,cash_usd_try, rub_try, cash_rub_try,try_rub,usd_thb,cash_usd_thb,rub_thb,cash_rub_thb)
        except Exception as e:
            logger.error(f"Ошибка с добавлением курса:{e}!!!")
            return None
        self.set_currency(rates)
        return api_courses

    def set_currency(self, rates:tuple, time=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")):
        with self.get_connection() as conn:
            c = conn.cursor()
            logger.info("Вставляем курсы в таблицу...")
            c.execute('''INSERT INTO currency (usd_rub, rub_usd, usd_try,cash_usd_try, rub_try, cash_rub_try, try_rub, 
             usd_thb, cash_usd_thb, rub_thb, cash_rub_thb, updated_at) 
             VALUES (?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (*rates, time))
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

    def get_coef(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            logger.info("Подтягиваем наценку из таблицы...")
            c.execute("SELECT * FROM coef")

            rows = c.fetchall()
            logger.info("Подтянули наценку, даем!")
            return rows




if __name__ == "__main__":
   qdb=QueueDB()
   qdb.update_currency()
   print(qdb.get_currencies())



