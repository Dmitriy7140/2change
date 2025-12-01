
import datetime
import sqlite3
from contextlib import contextmanager
from utils import logger


class QueueDB:
    def __init__(self, path_to_db="database.db"):
        self.db_path = path_to_db
        self._init_db()

    def _init_db(self):
        with self.get_connection() as conn:
            c = conn.cursor()  # ✅ Добавлены ()
            c.execute('''CREATE TABLE IF NOT EXISTS queue (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tg_id INTEGER UNIQUE,
                        country INTEGER,
                        name TEXT,
                        amount INTEGER,
                        currency1 TEXT,
                        currency2 TEXT,
                        reason TEXT,
                        created_at TEXT)''')
            conn.commit()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        try:
            yield conn
        finally:
            conn.close()

    def add_to_queue(self,  tg_id, name, country=1,reason=None, amount=None, currency1=None,
                     currency2=None, time=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")):
        with self.get_connection() as conn:
            c = conn.cursor()  # ✅ Исправлено
            c.execute('SELECT 1 FROM queue WHERE tg_id = ?', (tg_id,))
            if c.fetchone():
                logger.warning(f"Игнорировано: tg_id={tg_id} уже существует")
                return False

            if reason:
                c.execute('INSERT INTO queue (country, tg_id, name, reason, created_at) VALUES (?, ?, ?, ?, ?)',
                          (country, tg_id, name, reason, time))
            elif amount:
                if currency1 and currency2:
                    c.execute(
                        'INSERT INTO queue (country,tg_id, name, amount, currency1, currency2, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (country, tg_id, name, amount, currency1, currency2, time))
                elif currency1:
                    c.execute('INSERT INTO queue (country, tg_id, name, amount, currency1, created_at) VALUES (?,?, ?, ?, ?, ?)',
                              (country, tg_id, name, amount, currency1, time))
                elif currency2:
                    c.execute('INSERT INTO queue (country, tg_id, name, amount, currency2, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                              (country,tg_id, name, amount, currency2, time))
                else:
                    c.execute('INSERT INTO queue (country, tg_id, name, amount, created_at) VALUES (?, ?, ?, ?, ?)',
                              (country,tg_id, name, amount, time))
            else:
                return False

            conn.commit()
            logger.info(f"{name} (ID {tg_id}) добавлен в очередь.")
            return True

    def get_from_queue(self):
        """Берёт последнюю запись из очереди, удаляет её в БД и возвращает как кортеж.
            Если записей нет — возвращает None.
            """
        with self.get_connection() as conn:
            c = conn.cursor()

            # 1. Берём последнюю запись
            c.execute("SELECT * FROM queue ORDER BY id DESC LIMIT 1")
            row = c.fetchone()

            if row is None:
                logger.info("Записей не осталось")
                return None

            # row = (id, tg_id, country, name, amount, currency1, currency2, reason, created_at)
            last_id = row[0]

            # 2. Удаляем именно её
            c.execute("DELETE FROM queue WHERE id = ?", (last_id,))
            conn.commit()

            logger.info(f"Извлечена и удалена запись с id={last_id}")
            print(row)
            return row  # кортеж со всеми полями, None сохраняются как есть

    def count_rows(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM queue")
            count = c.fetchone()[0]
        return count


