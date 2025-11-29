# import datetime
# import sqlite3
# from contextlib import contextmanager
#
#
#
# from utils import logger
#
# class QueueDB:
#     def __init__(self, path_to_db="database.db"):
#         self.db_path=path_to_db
#         self._init_db()
#     def _init_db(self):
#         with self.get_connection() as conn:
#             c = conn.cursor()
#             c.execute('''CREATE TABLE IF NOT EXISTS queue (
#                         id INTEGER PRIMARY KEY AUTOINCREMENT,
#                         tg_id INTEGER UNIQUE,
#                         name TEXT,
#                         amount INTEGER NULLABLE,
#                         currency1 TEXT NULLABLE,
#                         currency2 TEXT NULLABLE,
#                         reason TEXT NULLABLE,
#                         created_at TEXT)''')
#             conn.commit()
#     @contextmanager
#     def get_connection(self):
#         conn= sqlite3.connect(self.db_path, check_same_thread=False)
#         try:
#             yield conn
#         finally:
#             conn.close()
#
#
#
#
#     def add_to_queue(self, tg_id, name, reason=None,amount=None,currency1=None,currency2=None, time=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")):
#
#         with self.get_connection() as conn:
#             c = conn.cursor()
#             c.execute('SELECT 1 FROM queue WHERE tg_id = ?', (tg_id,))
#             if c.fetchone():
#                 logger.warning(f"Игнорировано: tg_id={tg_id} уже существует")
#                 return False
#             if reason:
#                 c.execute('INSERT INTO queue (tg_id, name, reason, created_at) VALUES (?, ?, ?, ?)',
#                           (tg_id, name, reason, time))
#                 conn.commit()
#                 logger.info(f"{name} (ID {tg_id}) добавлен в очередь. Не обмен.")
#                 return True
#             elif amount:
#                 if currency1 and currency2:
#                     c.execute('INSERT INTO queue (tg_id, name, amount, currency1, currency2, created_at) VALUES (?, ?, ?, ?, ?, ?)',
#                               (tg_id, name, amount, currency1, currency2, time))
#                     conn.commit()
#                     logger.info(f"{name} (ID {tg_id}) добавлен в очередь. Обмен.")
#                 elif currency1 and not currency2:
#
#                     c.execute(
#                         'INSERT INTO queue (tg_id, name, amount, currency1, created_at) VALUES (?, ?, ?, ?, ?)',
#                         (tg_id, name, amount, currency1, time))
#                     conn.commit()
#                     logger.info(f"{name} (ID {tg_id}) добавлен в очередь. Обмен.")
#                 elif not currency1 and currency2:
#
#                     c.execute(
#                         'INSERT INTO queue (tg_id, name, amount, currency2, created_at) VALUES (?,  ?, ?, ?, ?)',
#                         (tg_id, name, amount, currency2, time))
#                     conn.commit()
#                     logger.info(f"{name} (ID {tg_id}) добавлен в очередь. Обмен.")
#
#             return False
#
#     def get_from_queue(self):
#         """Возвращает из очереди 4 переменных или None
#
#         :return: None - если не было людей в очереди
#         :return List with tuples - Если есть люди в очереди. В них - Айди телеграм, Имя с фаамилией, причина заявления, и когда было отправлено"""
#
#
#
#         queue_array=[]
#         with self.get_connection() as conn:
#             c= conn.cursor()
#             while True:
#                 c.execute("SELECT * FROM queue ORDER BY id DESC LIMIT 1")
#
#                 row = c.fetchone()
#                 if row:
#
#                     _, tg_id, name, reason, crated_at, = row
#                     c.execute('DELETE FROM queue WHERE tg_id = ?', (tg_id,))
#                     conn.commit()
#                     line=( tg_id, name, reason, crated_at)
#                     queue_array.append(line)
#                     logger.info(f"{tg_id} добавлен в очередь.")
#                 else:
#                     logger.info("Записей не осталось")
#                     return queue_array if queue_array else None
#
#

# if __name__ == '__main__':
    # add_to_queue(55, "ссан", "хочу помр")
    # print(get_from_queue())
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

    def add_to_queue(self, tg_id, name, reason=None, amount=None, currency1=None,
                     currency2=None, time=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")):
        with self.get_connection() as conn:
            c = conn.cursor()  # ✅ Исправлено
            c.execute('SELECT 1 FROM queue WHERE tg_id = ?', (tg_id,))
            if c.fetchone():
                logger.warning(f"Игнорировано: tg_id={tg_id} уже существует")
                return False

            if reason:
                c.execute('INSERT INTO queue (tg_id, name, reason, created_at) VALUES (?, ?, ?, ?)',
                          (tg_id, name, reason, time))
            elif amount:
                if currency1 and currency2:
                    c.execute(
                        'INSERT INTO queue (tg_id, name, amount, currency1, currency2, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                        (tg_id, name, amount, currency1, currency2, time))
                elif currency1:
                    c.execute('INSERT INTO queue (tg_id, name, amount, currency1, created_at) VALUES (?, ?, ?, ?, ?)',
                              (tg_id, name, amount, currency1, time))
                elif currency2:
                    c.execute('INSERT INTO queue (tg_id, name, amount, currency2, created_at) VALUES (?, ?, ?, ?, ?)',
                              (tg_id, name, amount, currency2, time))
                else:
                    c.execute('INSERT INTO queue (tg_id, name, amount, created_at) VALUES (?, ?, ?, ?)',
                              (tg_id, name, amount, time))
            else:
                return False

            conn.commit()
            logger.info(f"{name} (ID {tg_id}) добавлен в очередь.")
            return True

    def get_from_queue(self):
        """Возвращает список записей из очереди или None"""
        with self.get_connection() as conn:
            c = conn.cursor()  # ✅ Исправлено
            c.execute("SELECT tg_id, name, reason, created_at FROM queue ORDER BY id DESC")
            rows = c.fetchall()

            if not rows:
                logger.info("Записей не осталось")
                return None

            # Удаляем все записи одной командой
            tg_ids = [row[0] for row in rows]
            c.executemany('DELETE FROM queue WHERE tg_id = ?', [(tid,) for tid in tg_ids])
            conn.commit()

            logger.info(f"Извлечено {len(rows)} записей из очереди")
            return rows  # [(tg_id, name, reason, created_at), ...]



