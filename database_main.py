import datetime
import sqlite3

from utils import logger

conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER UNIQUE,
            name TEXT,
            
            reason TEXT,
            created_at TEXT)''')
conn.commit()

def add_to_queue(tg_id, name, reason, time=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")):
    c.execute('SELECT 1 FROM queue WHERE tg_id = ?', (tg_id,))
    if c.fetchone():
        logger.warning(f"Игнорировано добавление: запись с tg_id={tg_id} уже существует.")
    else:
        c.execute(
            'INSERT INTO queue (tg_id, name, reason, created_at) VALUES (?, ?, ?, ?)',
            (tg_id, name, reason, time)
        )
        conn.commit()
        logger.info(f"{name} с айди {tg_id} добавлен в очередь!")
def get_from_queue():
    """Возвращает из очереди 4 переменных или None

    :return: None - если не осталось людей в очереди
    :return tuple with 4 values - Айди телеграм, Имя с фаамилией, причина заявления, и когда было отправлено"""

    c.execute("SELECT * FROM queue ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    if row:
        _, tg_id, name, reason, crated_at, = row
        c.execute('DELETE FROM queue WHERE tg_id = ?', (tg_id,))
        conn.commit()
        return tg_id, name, reason, crated_at
    else:
        logger.info("Записей не осталось")
        return None



if __name__ == '__main__':
    # add_to_queue(23231213, "Игнат","арбакайте")
    print(get_from_queue())


