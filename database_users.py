import sqlite3
from datetime import datetime, timedelta, timezone
from utils import logger


def now_utc():
    return datetime.now(timezone.utc)


class UserDB:
    def __init__(self, db_path="database.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()



    def _create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            source TEXT,
            state TEXT,
            first_login TEXT,
            last_seen TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS links (
            link TEXT PRIMARY KEY,
            followed INTEGER DEFAULT 0
        )
        """)

        self.conn.commit()


    # ---------------- USERS ----------------
    def get_links(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM links
        """)
        links = cursor.fetchall()
        return links
    def get_users(self):


        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = [dict(row) for row in cursor.fetchall()]

        logger.info(f"Получено пользователей: {len(rows)}")
        return rows

    def get_users_by_source(self, source):


        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE source = ?",
            (source,)
        )
        rows = [dict(row) for row in cursor.fetchall()]

        logger.info(f"Найдено пользователей по source={source}: {len(rows)}")
        return rows

    def get_users_by_state(self, state):


        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE state = ?",
            (state,)
        )
        rows = [dict(row) for row in cursor.fetchall()]

        logger.info(f"Найдено пользователей по state={state}: {len(rows)}")
        return rows

    # ---------------- ADD USER ----------------

    def add_user(self, telegram_id: int, source: str | None = None, state: str | None = None):
        """possible states  
            "announce_tr": "turkey",
            "announce_vn": "vietnam",
            "announce_kr": "korea",
            "announce_ru": "russia",
            "announce_cn": "china",
        }"""


        cursor = self.conn.cursor()
        now = now_utc().isoformat()

        cursor.execute(
            "SELECT telegram_id FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        user_exists = cursor.fetchone()

        if user_exists:
            cursor.execute("""
                UPDATE users
                SET state = ?, last_seen = ?
                WHERE telegram_id = ?
            """, (state, now, telegram_id))

            logger.info(f"Обновлён last_seen пользователя {telegram_id}")

        else:
            cursor.execute("""
                INSERT INTO users (telegram_id, source, state, first_login, last_seen)
                VALUES (?, ?, ?, ?, ?)
            """, (telegram_id, source, state, now, now))

            logger.info(f"Создан новый пользователь {telegram_id}")

            # обработка реферальной ссылки
            if source:
                cursor.execute(
                    "SELECT followed FROM links WHERE link = ?",
                    (source,)
                )
                link = cursor.fetchone()

                if link:
                    cursor.execute("""
                        UPDATE links
                        SET followed = followed + 1
                        WHERE link = ?
                    """, (source,))

                    logger.info(f"Реферал обновлён: {source}")

                else:
                    cursor.execute("""
                        INSERT INTO links (link, followed)
                        VALUES (?, 1)
                    """, (source,))

                    logger.info(f"Новая реферальная ссылка добавлена: {source}")

        self.conn.commit()
        logger.info("Изменения сохранены в БД")

    # ---------------- STATE ----------------

    def update_state(self, telegram_id: int, state: str):
        logger.info(f"Обновление state пользователя {telegram_id} -> {state}")

        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE users
            SET state = ?
            WHERE telegram_id = ?
        """, (state, telegram_id))

        self.conn.commit()
        logger.info(f"State обновлён для {telegram_id}")

    # ---------------- ACTIVITY ----------------

    def get_active_users(self, days=21):
        logger.info(f"Запрос активных пользователей за {days} дней")

        threshold = (now_utc() - timedelta(days=days)).isoformat()

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM users
            WHERE last_seen >= ?
        """, (threshold,))

        rows = [dict(row) for row in cursor.fetchall()]

        logger.info(f"Активных пользователей: {len(rows)}")
        return rows

    def get_inactive_users(self, days=21):
        logger.info(f"Запрос НЕактивных пользователей за {days} дней")

        threshold = (now_utc() - timedelta(days=days)).isoformat()

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM users
            WHERE last_seen < ?
        """, (threshold,))

        rows = [dict(row) for row in cursor.fetchall()]

        logger.info(f"Неактивных пользователей: {len(rows)}")
        return rows


    def track_start(self):
        def decorator(func):
            def wrapper(message, *args, **kwargs):

                user_id = message.from_user.id
                source = None

                if message.text:
                    parts = message.text.split()
                    if len(parts) > 1:
                        source = parts[1]
                        # deep-link из /menulink: payload = <menu_key>__<источник>
                        # в аналитику пишем только источник (часть после "__")
                        if source and "__" in source:
                            source = source.split("__", 1)[1]

                self.add_user(
                    telegram_id=user_id,
                    source=source
                )

                return func(message, *args, **kwargs)

            return wrapper
        return decorator
    def track_user(self, state=None):
        def decorator(func):
            def wrapper(update, *args, **kwargs):

                user = getattr(update, "from_user", None)

                if not user and hasattr(update, "message"):
                    user = update.message.from_user

                if not user:
                    return func(update, *args, **kwargs)

                self.add_user(
                    telegram_id=user.id,
                    source=None,
                    state= state,
                )

                return func(update, *args, **kwargs)

            return wrapper
        return decorator