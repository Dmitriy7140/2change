from decimal import Decimal
from typing import Any

import coinoxr
import datetime
import sqlite3
from contextlib import contextmanager
from utils import logger
from config import API_KEY
from datetime import datetime, timedelta

from api.rapira import RapiraAPI
from api.binance import BinanceAPI
from api.btcturk import get_usdt_try
from api.bitkub import get_usdt_thb
from api.kraken import KrakenAPI
rapira = RapiraAPI()
binance = BinanceAPI()
kraken = KrakenAPI()



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
                
                rub_cny REAL,
                usd_cny REAL,
                cny_rub REAL,
                
                usd_krw REAL,
                krw_usd REAL,
                rub_krw REAL,
                krw_rub REAL,
                usd_vnd REAL,
                cash_usd_vnd REAL,
                rub_vnd REAL,
                cash_rub_vnd REAL,
                vnd_rub REAL,
                rub_eur REAL,
                eur_rub REAL,
                usd_eur REAL,
                eur_usd REAL,
                rub_gel REAL,
                usdt_gel REAL,
                gel_rub REAL,
                updated_at TIMESTAMP)''')
            logger.info("Таблица с курсами загружена...")

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
                            
                            rub_cny_c REAL,
                            usd_cny_c REAL,
                            cny_rub_c REAL,
                            
                            usd_krw_c REAL,
                            krw_usd_c REAL,
                            rub_krw_c REAL,
                            krw_rub_c REAL,
                            
                            usd_vnd_c REAL,
                            cash_usd_vnd_c REAL,
                            rub_vnd_c REAL,
                            cash_rub_vnd_c REAL,
                            vnd_rub_c REAL,
                            rub_eur_c REAL,
                            eur_rub_c REAL,
                            usd_eur_c REAL,
                            eur_usd_c REAL,
                            rub_gel_c REAL,
                            usdt_gel_c REAL,
                            gel_rub_c REAL,
                            updated_at TEXT)''')
            logger.info("Таблица с наценкой загружена...")

            # --- МИГРАЦИЯ: vnd_rub / vnd_rub_c сразу после cash_rub_vnd(_c) ---
            # ALTER TABLE в SQLite добавляет столбец только в конец, что ломает
            # позиционное чтение и порядок в таблице interest, поэтому пересоздаём.
            self._migrate_add_vnd_rub(c)
            # --- МИГРАЦИЯ: евро-курсы перед updated_at ---
            self._migrate_add_eur(c)
            # --- МИГРАЦИЯ: курсы GEL перед updated_at ---
            self._migrate_add_gel(c)

            c.execute("SELECT COUNT(*) FROM coef")
            count = c.fetchone()[0]
            c.execute('''CREATE TABLE IF NOT EXISTS id_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message_id INTEGER,
                        user_id INTEGER,
                        user_ref TEXT)''')

            if count == 0:  # Только если таблица пустая
                c.execute('''INSERT INTO coef (usd_rub_c,
                 rub_usd_c,
                 
                usd_try_c,
                cash_usd_try_c,
                rub_try_c,
                cash_rub_try_c,
                try_rub_c,
                
                usd_thb_c, 
                cash_usd_thb_c,
                rub_thb_c,
                cash_rub_thb_c,
                
                rub_cny_c, 
                usd_cny_c,
                cny_rub_c,
                
                usd_krw_c,
                krw_usd_c,
                rub_krw_c,
                krw_rub_c,
                
                usd_vnd_c,
                cash_usd_vnd_c,
                rub_vnd_c,
                cash_rub_vnd_c,
                vnd_rub_c,
                rub_eur_c,
                eur_rub_c,
                usd_eur_c,
                eur_usd_c,
                rub_gel_c,
                usdt_gel_c,
                gel_rub_c,
                updated_at)
                 VALUES (0.04,
                     0.075,
                     
                     0.07,
                     0.07,  
                     0.09, 
                     0.22,   
                     0.11,
                        
                     0.05,  
                     0.05, 
                     0.11, 
                     0.12,
                      
                     0.08, 
                     0.05,
                     0.10,
                     
                     0.05,
                     0.06,
                     0.06,
                     0.10,
                     
                     0.06,
                     0.06,
                     0.10,
                     0.10,
                     0.04,
                     0.01,
                     0.01,
                     0.01,
                     0.01,
                     0.01,
                     0.01,
                     0.01,
                         ?)''', ("default",))

                logger.info("Начальные коэффициенты добавлены")
            else:
                logger.info(f"Таблица с наценкой уже содержит {count} записей, пропуск INSERT")


            conn.commit()
            logger.info("Создали БД! Ну, или проверили что она на месте!")

    def _migrate_add_vnd_rub(self, c):
        """Добавляет vnd_rub_c в coef и vnd_rub в currency сразу после
        cash_rub_vnd(_c). Для свежих БД (столбцы уже есть) — ничего не делает."""

        # --- coef: пересоздаём, сохраняя коэффициенты ---
        c.execute("PRAGMA table_info(coef)")
        coef_cols = [row[1] for row in c.fetchall()]
        if "vnd_rub_c" not in coef_cols:
            logger.info("Миграция coef: добавляем vnd_rub_c")
            c.execute("ALTER TABLE coef RENAME TO coef_old")
            c.execute('''CREATE TABLE coef (
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
                            rub_cny_c REAL,
                            usd_cny_c REAL,
                            cny_rub_c REAL,
                            usd_krw_c REAL,
                            krw_usd_c REAL,
                            rub_krw_c REAL,
                            krw_rub_c REAL,
                            usd_vnd_c REAL,
                            cash_usd_vnd_c REAL,
                            rub_vnd_c REAL,
                            cash_rub_vnd_c REAL,
                            vnd_rub_c REAL,
                            updated_at TEXT)''')
            c.execute('''INSERT INTO coef (
                id, usd_rub_c, rub_usd_c, usd_try_c, cash_usd_try_c, rub_try_c,
                cash_rub_try_c, try_rub_c, usd_thb_c, cash_usd_thb_c, rub_thb_c,
                cash_rub_thb_c, rub_cny_c, usd_cny_c, cny_rub_c, usd_krw_c,
                krw_usd_c, rub_krw_c, krw_rub_c, usd_vnd_c, cash_usd_vnd_c,
                rub_vnd_c, cash_rub_vnd_c, vnd_rub_c, updated_at)
                SELECT
                id, usd_rub_c, rub_usd_c, usd_try_c, cash_usd_try_c, rub_try_c,
                cash_rub_try_c, try_rub_c, usd_thb_c, cash_usd_thb_c, rub_thb_c,
                cash_rub_thb_c, rub_cny_c, usd_cny_c, cny_rub_c, usd_krw_c,
                krw_usd_c, rub_krw_c, krw_rub_c, usd_vnd_c, cash_usd_vnd_c,
                rub_vnd_c, cash_rub_vnd_c, 0.04, updated_at
                FROM coef_old''')
            c.execute("DROP TABLE coef_old")
            logger.info("Миграция coef завершена (vnd_rub_c=0.04 по умолчанию)")

        # --- currency: курсы эфемерны (обновляются каждые 20 мин) — просто
        #     пересоздаём с vnd_rub после cash_rub_vnd, следующий update заполнит ---
        c.execute("PRAGMA table_info(currency)")
        cur_cols = [row[1] for row in c.fetchall()]
        if "vnd_rub" not in cur_cols:
            logger.info("Миграция currency: добавляем vnd_rub")
            c.execute("DROP TABLE currency")
            c.execute('''CREATE TABLE currency (
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
                rub_cny REAL,
                usd_cny REAL,
                cny_rub REAL,
                usd_krw REAL,
                krw_usd REAL,
                rub_krw REAL,
                krw_rub REAL,
                usd_vnd REAL,
                cash_usd_vnd REAL,
                rub_vnd REAL,
                cash_rub_vnd REAL,
                vnd_rub REAL,
                updated_at TIMESTAMP)''')
            logger.info("Миграция currency завершена")

    def _migrate_add_eur(self, c):
        """Добавляет евро-курсы (usd_eur/eur_usd/rub_eur/eur_rub + коэффициенты)
        перед updated_at. Значения коэффициентов сохраняются (читаем строку как
        словарь), новые = 0.04. currency эфемерна — просто пересоздаём. Идемпотентно."""
        eur_coef = ["rub_eur_c", "eur_rub_c", "usd_eur_c", "eur_usd_c"]
        eur_cur = ["rub_eur", "eur_rub", "usd_eur", "eur_usd"]

        # --- coef: пересоздаём, сохраняя все текущие коэффициенты ---
        c.execute("PRAGMA table_info(coef)")
        cols = [row[1] for row in c.fetchall()]
        if "usd_eur_c" not in cols:
            logger.info("Миграция coef: добавляем евро-коэффициенты")
            c.execute("SELECT * FROM coef LIMIT 1")
            row = c.fetchone()
            old = dict(zip(cols, row)) if row else {}
            base = [x for x in cols if x not in ("id", "updated_at")]
            final = base + eur_coef
            c.execute("DROP TABLE coef")
            c.execute("CREATE TABLE coef (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                      + ", ".join(f"{n} REAL" for n in final) + ", updated_at TEXT)")
            values = [old.get(n, 0.01) for n in final]  # старые из old, евро = 0.01
            c.execute("INSERT INTO coef (id, " + ", ".join(final) + ", updated_at) VALUES (1, "
                      + ", ".join("?" for _ in final) + ", ?)",
                      (*values, old.get("updated_at", "migrated")))
            logger.info("Миграция coef (евро) завершена, наценки 0.01 по умолчанию")

        # --- currency: эфемерна, пересоздаём в актуальном виде ---
        c.execute("PRAGMA table_info(currency)")
        ccols = [row[1] for row in c.fetchall()]
        if "usd_eur" not in ccols:
            logger.info("Миграция currency: добавляем евро-курсы")
            base = [x for x in ccols if x not in ("id", "updated_at")]
            final = base + eur_cur
            c.execute("DROP TABLE currency")
            c.execute("CREATE TABLE currency (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                      + ", ".join(f"{n} REAL" for n in final) + ", updated_at TIMESTAMP)")
            logger.info("Миграция currency (евро) завершена")

    def _migrate_add_gel(self, c):
        """Добавляет курсы GEL и их наценки, не изменяя прежние значения."""
        gel_coef = ["rub_gel_c", "usdt_gel_c", "gel_rub_c"]
        gel_cur = ["rub_gel", "usdt_gel", "gel_rub"]

        c.execute("PRAGMA table_info(coef)")
        coef_cols = [row[1] for row in c.fetchall()]
        if not all(name in coef_cols for name in gel_coef):
            logger.info("Миграция coef: добавляем наценки GEL")
            c.execute("SELECT * FROM coef LIMIT 1")
            row = c.fetchone()
            old = dict(zip(coef_cols, row)) if row else {}
            base = [name for name in coef_cols if name not in ("id", "updated_at")]
            final = base + [name for name in gel_coef if name not in base]
            c.execute("DROP TABLE coef")
            c.execute("CREATE TABLE coef (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                      + ", ".join(f"{name} REAL" for name in final)
                      + ", updated_at TEXT)")
            values = [old.get(name, 0.01) for name in final]
            c.execute("INSERT INTO coef (id, " + ", ".join(final)
                      + ", updated_at) VALUES (1, "
                      + ", ".join("?" for _ in final) + ", ?)",
                      (*values, old.get("updated_at", "migrated")))
            logger.info("Миграция coef (GEL) завершена, наценки 0.01 по умолчанию")

        c.execute("PRAGMA table_info(currency)")
        cur_cols = [row[1] for row in c.fetchall()]
        if not all(name in cur_cols for name in gel_cur):
            logger.info("Миграция currency: добавляем курсы GEL")
            c.execute("SELECT * FROM currency")
            old_rows = c.fetchall()
            base = [name for name in cur_cols if name not in ("id", "updated_at")]
            final = base + [name for name in gel_cur if name not in base]
            c.execute("DROP TABLE currency")
            c.execute("CREATE TABLE currency (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                      + ", ".join(f"{name} REAL" for name in final)
                      + ", updated_at TIMESTAMP)")

            # Сохраняем историю курсов при миграции. Для новой обратной пары
            # восстанавливаем базовый курс из RUB→GEL и применяем наценку в
            # противоположную сторону.
            c.execute("SELECT rub_gel_c, gel_rub_c FROM coef WHERE id = 1")
            rub_gel_c, gel_rub_c = c.fetchone()
            for old_row in old_rows:
                old = dict(zip(cur_cols, old_row))
                values = []
                for name in final:
                    if name == "gel_rub" and old.get("rub_gel") is not None:
                        raw_gel_rub = old["rub_gel"] / (1 + rub_gel_c)
                        values.append(raw_gel_rub * (1 - gel_rub_c))
                    else:
                        values.append(old.get(name))
                c.execute("INSERT INTO currency (id, " + ", ".join(final)
                          + ", updated_at) VALUES (?, "
                          + ", ".join("?" for _ in final) + ", ?)",
                          (old["id"], *values, old.get("updated_at")))
            logger.info("Миграция currency (GEL) завершена")

    @contextmanager
    def get_connection(self):

        conn = sqlite3.connect(self.db_path, check_same_thread=False)

        try:

            yield conn
        finally:

            conn.close()

    def add_to_queue(self, tg_id, name, country=1, reason=None,
                     amount1=None, amount2=None, currency1=None,
                     currency2=None, time=None):

        if time is None:
            time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
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
                        'INSERT INTO queue (country,tg_id, name, amount1, amount2, currency1, currency2, created_at) VALUES (?, ?, ?,?, ?, ?, ?, ?)',
                        (country, tg_id, name, amount1, amount2, currency1, currency2, time))
                    logger.info("В очередь добавлена заявка на обмен, обе валюты известны!")

            else:
                logger.info("Что-то пошло не так при добавлении пользователя в очередь!!!")
                return False

            conn.commit()

            logger.info(f"{name} (ID {tg_id}) добавлен в очередь.")
            return True

    def get_from_queue(self, to_confirm:bool=False, get_by_id:int=None):
        """Берёт последнюю запись из очереди, удаляет её в БД и возвращает как кортеж.
            Если записей нет — возвращает None.
            """
        with self.get_connection() as conn:
            c = conn.cursor()
            if to_confirm:
                c.execute("SELECT * FROM queue ORDER BY id DESC")
                rows = c.fetchall()
                return rows
            if get_by_id:
                c.execute("SELECT * FROM queue WHERE tg_id = ?", (get_by_id,))
                row = c.fetchone()
                c.execute("DELETE FROM queue WHERE tg_id = ?", (get_by_id,))
                conn.commit()
                return row

            logger.info("Подтягиваем последнюю запись из очереди...")
            # 1. Берём последнюю запись
            c.execute("SELECT * FROM queue ORDER BY id DESC LIMIT 1")
            row = c.fetchone()


            if row is None:
                logger.info("Записей не осталось!")
                return None

            # row = (id, tg_id, country, name, amount, currency1, currency2, reason, created_at)

            last_id = row[0]

            # 2. Удаляем именно её
            c.execute("DELETE FROM queue WHERE id = ?", (last_id,))
            logger.info("Удалили запись из очереди...")

            conn.commit()

            logger.info(f"Извлечена и удалена запись с id={last_id}!")

            return row  # кортеж со всеми полями, None сохраняются как есть

    def count_rows(self):
        with self.get_connection() as conn:
            c = conn.cursor()

            c.execute("SELECT COUNT(*) FROM queue")
            count = c.fetchone()[0]
            logger.info(f"Посчитали, что осталось {count} заявок!")
        return count

    def ensure_currency_fresh(self):
        """
        🔹 Проверяет, нужно ли обновить курсы
        🔹 Обновляет, если прошло > 3 часов
        """

        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT updated_at
                         FROM currency
                         ORDER BY id DESC LIMIT 1''')

            row = c.fetchone()

        # 🔹 1. Если курсов вообще нет
        if not row:
            logger.info("Курсов нет — обновляем")
            self.update_currency()
            return

        updated_at = datetime.strptime(row[0], "%d-%m-%Y %H:%M:%S.%f")
        now = datetime.now()

        # 🔹 2. Проверка на устаревание
        if now - updated_at > timedelta(minutes=20):
            logger.info("Курсы устарели (>3ч) — обновляем")
            self.update_currency()
        else:
            logger.info("Курсы свежие — обновление не требуется")

    def _get_latest_usdt_gel(self):
        """Возвращает последний курс USDT/GEL после наценки, без обновления БД."""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("""SELECT usdt_gel
                         FROM currency
                         WHERE usdt_gel IS NOT NULL
                         ORDER BY id DESC
                         LIMIT 1""")
            row = c.fetchone()
        return row[0] if row else None

    def update_currency(self):

        """:return api_courses= {"usd_try":api_usd_try,
                          "usd_rub":api_usd_rub,
                          "usd_thb":api_usd_thb,
                          "try_rub":api_try_rub,
                          "thb_rub":api_thb_rub} """
        try:
            coinoxr.app_id = API_KEY
            logger.info("Подсосались к апи...")

            all_courses = coinoxr.Latest().get(base=f"USD", show_alternative=True)
            api_usd_try = get_usdt_try()
            rapira_usdt_rub = rapira.get_usdt_rub()
            api_rub_usd = rapira_usdt_rub["askPrice"]
            api_usd_rub = rapira_usdt_rub["bidPrice"]
            api_usd_thb = get_usdt_thb()
            api_vnd_usd = all_courses.body["rates"]["VND"]
            api_usd_cny = all_courses.body["rates"]["CNY"]
            api_krw_usd = all_courses.body["rates"]["KRW"]
            # отдельный запрос base=VND — прямой сырой курс донг→рубль из OXR (RUB за 1 донг ≈ 0.0030)
            vnd_courses = coinoxr.Latest().get(base="VND", show_alternative=True)
            api_vnd_rub = vnd_courses.body["rates"]["RUB"]
            api_usd_eur = kraken.get_usdt_eur()["last"]  # EUR за 1 USDT (~0.87), Kraken
            api_usdt_gel = binance.get_second_best_usdt_gel_sell_price()
            rows_list= self.get_coef()
            rows = rows_list[0]

            if api_usdt_gel is None:
                previous_usdt_gel = self._get_latest_usdt_gel()
                if previous_usdt_gel is None:
                    raise ValueError("Binance P2P returned no USDT/GEL prices and no cached rate exists")

                usdt_gel_multiplier = Decimal("1") - Decimal(str(rows[29]))
                if usdt_gel_multiplier <= 0:
                    raise ValueError("USDT/GEL markup must be less than 100% to restore cached rate")

                # В БД хранится цена уже после наценки. Восстанавливаем сырую
                # цену так, чтобы итоговая цена в рассылке осталась прежней.
                api_usdt_gel = Decimal(str(previous_usdt_gel)) / usdt_gel_multiplier
                logger.warning("Binance P2P returned no USDT/GEL prices; using cached rate")

            # RUB за 1 GEL: RUB за 1 USDT (Rapira) / GEL за 1 USDT (Binance P2P).
            api_rub_gel = Decimal(str(api_rub_usd)) / api_usdt_gel
            logger.info("Подтянули доллар!")


            r = {"usd_rub":api_usd_rub,
                           "rub_usd":api_rub_usd,

                           "usd_try":api_usd_try,
                           "cash_usd_try":api_usd_try,
                           "rub_try":api_rub_usd/api_usd_try,
                           "cash_rub_try":api_rub_usd/api_usd_try,
                           "try_rub":api_rub_usd/api_usd_try,

                           "usd_thb": api_usd_thb,
                           "cash_usd_thb": api_usd_thb,
                           "rub_thb": api_rub_usd/api_usd_thb,
                           "cash_rub_thb": api_rub_usd/api_usd_thb,

                           "rub_cny": api_rub_usd / api_usd_cny,
                           "usd_cny": api_usd_cny,
                           "cny_rub": api_rub_usd/api_usd_cny,

                           "usd_krw": api_krw_usd,
                           "krw_usd": api_krw_usd,
                           "rub_krw": api_krw_usd/api_rub_usd,
                           "krw_rub": api_krw_usd/api_rub_usd,

                           "usd_vnd": api_vnd_usd,
                           "cash_usd_vnd": api_vnd_usd,
                           "rub_vnd": api_vnd_usd/api_rub_usd,
                           "cash_rub_vnd": api_vnd_usd/api_rub_usd,
                           # прямой сырой курс из OXR (base=VND): RUB за 1 донг
                           "vnd_rub": api_vnd_rub,

                           # ЕВРО (USDT-мост: api_usd_eur = EUR за 1 USDT, api_rub_usd = RUB за 1 USDT)
                           # RUB↔EUR считаем в РУБЛЯХ ЗА 1 ЕВРО (≈90), чтобы не возиться с нулями
                           "rub_eur": api_rub_usd / api_usd_eur,   # RUB→EUR: руб за 1 евро (делится)
                           "eur_rub": api_rub_usd / api_usd_eur,   # EUR→RUB: руб за 1 евро
                           "usd_eur": api_usd_eur,                 # USDT→EUR: EUR за 1 USDT
                           "eur_usd": api_usd_eur,                 # EUR→USDT: EUR за 1 USDT (делится)
                           "rub_gel": float(api_rub_gel),           # RUB за 1 GEL
                           "usdt_gel": float(api_usdt_gel),         # GEL за 1 USDT
                           "gel_rub": float(api_rub_gel),            # RUB за 1 GEL
                           }

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

                       "rub_cny_c": rows[12],
                       "usd_cny_c": rows[13],
                       "cny_rub_c": rows[14],

                       "usd_krw_c": rows[15],
                       "krw_usd_c": rows[16],
                       "rub_krw_c": rows[17],
                       "krw_rub_c": rows[18],
                       "usd_vnd_c": rows[19],
                       "cash_usd_vnd_c": rows[20],
                       "rub_vnd_c": rows[21],
                       "cash_rub_vnd_c": rows[22],
                       "vnd_rub_c": rows[23],
                       "rub_eur_c": rows[24],
                       "eur_rub_c": rows[25],
                       "usd_eur_c": rows[26],
                       "eur_usd_c": rows[27],
                       "rub_gel_c": rows[28],
                       "usdt_gel_c": rows[29],
                       "gel_rub_c": rows[30],

                       }

            usd_rub = r["usd_rub"] * (1 - we_sell["usd_rub_c"])
            rub_usd = r["rub_usd"] * (1 + we_sell["rub_usd_c"])

            # ЛИРЫ
            usd_try = r["usd_try"] * (1 - we_sell["usd_try_c"])
            cash_usd_try = r["cash_usd_try"] * (1 - we_sell["cash_usd_try_c"])
            rub_try = r["rub_try"] * (1 + we_sell["rub_try_c"])
            cash_rub_try = r["cash_rub_try"] * (1 + we_sell["cash_rub_try_c"])
            try_rub = r["try_rub"] * (1 - we_sell["try_rub_c"])
            logger.info("Посчитали лиры...")

            # БАТЫ
            usd_thb = r["usd_thb"] * (1 - we_sell["usd_thb_c"])
            cash_usd_thb = r["cash_usd_thb"] * (1 - we_sell["cash_usd_thb_c"])
            rub_thb = r["rub_thb"] * (1 + we_sell["rub_thb_c"])
            cash_rub_thb = r["cash_rub_thb"] * (1 + we_sell["cash_rub_thb_c"])
            logger.info("Посчитали баты...")
            # ЮАНИ
            rub_cny = r["rub_cny"] * (1 + we_sell["rub_cny_c"])
            usd_cny = r["usd_cny"] * (1 - we_sell["usd_cny_c"])
            cny_rub = r["cny_rub"] * (1 - we_sell["cny_rub_c"])
            logger.info("Посчитали юани...")
            # ВОНЫ
            krw_usd = r["krw_usd"] * (1 + we_sell["krw_usd_c"])
            krw_rub = r["krw_rub"] * (1 + we_sell["krw_rub_c"])
            usd_krw = r["usd_krw"] * (1 - we_sell["usd_krw_c"])
            rub_krw = r["rub_krw"] * (1 - we_sell["rub_krw_c"])
            logger.info("Посчитали воны...")


            # ДОНГИ
            usd_vnd = r["usd_vnd"] * (1 - we_sell["usd_vnd_c"])
            cash_usd_vnd = r["cash_usd_vnd"] * (1 - we_sell["cash_usd_vnd_c"])
            rub_vnd = r["rub_vnd"] * (1 - we_sell["rub_vnd_c"])
            cash_rub_vnd = r["cash_rub_vnd"] * (1 - we_sell["cash_rub_vnd_c"])
            # ДОНГИ → РУБЛИ (клиент отдаёт донги, получает рубли — даём меньше рублей)
            vnd_rub = r["vnd_rub"] * (1 - we_sell["vnd_rub_c"])
            logger.info("Посчитали донги...")

            # ЕВРО. rub_eur (руб за евро, покупка евро — дороже): +c, в конвертере делится.
            # eur_rub (руб за евро, продажа евро — дешевле): -c, в конвертере умножается.
            # usd_eur — умножаем (даём меньше EUR); eur_usd — делится (даём меньше USDT).
            rub_eur = r["rub_eur"] * (1 + we_sell["rub_eur_c"])
            eur_rub = r["eur_rub"] * (1 - we_sell["eur_rub_c"])
            usd_eur = r["usd_eur"] * (1 - we_sell["usd_eur_c"])
            eur_usd = r["eur_usd"] * (1 + we_sell["eur_usd_c"])
            logger.info("Посчитали евро...")

            # RUB↔GEL хранится как RUB за 1 GEL. Для RUB→GEL наценка увеличивает
            # цену лари, а для GEL→RUB — уменьшает сумму рублей для клиента.
            # USDT→GEL хранится как GEL за 1 USDT: наценка уменьшает результат.
            rub_gel = r["rub_gel"] * (1 + we_sell["rub_gel_c"])
            usdt_gel = r["usdt_gel"] * (1 - we_sell["usdt_gel_c"])
            gel_rub = r["gel_rub"] * (1 - we_sell["gel_rub_c"])
            logger.info("Посчитали лари...")



            rates = (usd_rub,
                     rub_usd,
                     usd_try,
                     cash_usd_try,
                     rub_try,
                     cash_rub_try,
                     try_rub,
                     usd_thb,
                     cash_usd_thb,
                     rub_thb,
                     cash_rub_thb,
                     rub_cny,
                     usd_cny,
                     cny_rub,
                     krw_usd,
                     krw_rub,
                     usd_krw,
                     rub_krw,
                     usd_vnd,
                     cash_usd_vnd,
                     rub_vnd,
                     cash_rub_vnd,
                     vnd_rub,
                     rub_eur,
                     eur_rub,
                     usd_eur,
                      eur_usd,
                      rub_gel,
                      usdt_gel,
                      gel_rub,)
        except Exception:
            logger.exception("Ошибка с добавлением курса")
            return None
        self.set_currency(rates)

        return  r

    def set_currency(self, rates:tuple):
        with self.get_connection() as conn:
            c = conn.cursor()

            c.execute('''INSERT INTO currency (usd_rub, rub_usd, usd_try,cash_usd_try, rub_try, cash_rub_try, try_rub,
             usd_thb, cash_usd_thb, rub_thb, cash_rub_thb, rub_cny, usd_cny, cny_rub,krw_usd, krw_rub, usd_krw, rub_krw,usd_vnd, cash_usd_vnd, rub_vnd, cash_rub_vnd, vnd_rub, rub_eur, eur_rub, usd_eur, eur_usd, rub_gel, usdt_gel, gel_rub, updated_at)
             VALUES (?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (*rates, datetime.now().strftime("%d-%m-%Y %H:%M:%S.%f")))

            conn.commit()


    def get_currencies(self, should_be_dict:bool=True) -> dict[str | Any, Any] | Any:

        """returns: latest currency row (tuple) + api currencies (dict)"""
        self.ensure_currency_fresh()

        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM currency ORDER BY id DESC LIMIT 1")
            row = c.fetchone()
        if should_be_dict:
            (
                _,
                usd_rub,
                rub_usd,
                usd_try,
                cash_usd_try,
                rub_try,
                cash_rub_try,
                try_rub,
                usd_thb,
                cash_usd_thb,
                rub_thb,
                cash_rub_thb,
                rub_cny,
                usd_cny,
                cny_rub,
                usd_krw,
                krw_usd,
                rub_krw,
                krw_rub,
                usd_vnd,
                cash_usd_vnd,
                rub_vnd,
                cash_rub_vnd,
                vnd_rub,
                rub_eur,
                eur_rub,
                usd_eur,
                eur_usd,
                rub_gel,
                usdt_gel,
                gel_rub,
                updated_at,
            ) = row
            return {
            "usd_rub": usd_rub,
            "rub_usd": rub_usd,
            "usd_try": usd_try,
            "cash_usd_try": cash_usd_try,
            "rub_try": rub_try,
            "cash_rub_try": cash_rub_try,
            "try_rub": try_rub,
            "usd_thb": usd_thb,
            "cash_usd_thb": cash_usd_thb,
            "rub_thb": rub_thb,
            "cash_rub_thb": cash_rub_thb,
            "rub_cny": rub_cny,
            "usd_cny": usd_cny,
            "cny_rub": cny_rub,
            "usd_krw": usd_krw,
            "krw_usd": krw_usd,
            "rub_krw": rub_krw,
            "krw_rub": krw_rub,
            "usd_vnd": usd_vnd,
            "cash_usd_vnd": cash_usd_vnd,
            "rub_vnd": rub_vnd,
            "cash_rub_vnd": cash_rub_vnd,
            "vnd_rub": vnd_rub,
            "rub_eur": rub_eur,
            "eur_rub": eur_rub,
            "usd_eur": usd_eur,
            "eur_usd": eur_usd,
            "rub_gel": rub_gel,
            "usdt_gel": usdt_gel,
            "gel_rub": gel_rub,
            "updated_at": updated_at,
                                }
        return row

    def get_coef(self):
        with self.get_connection() as conn:
            c = conn.cursor()

            c.execute("SELECT * FROM coef")

            rows = c.fetchall()

            return rows
    def set_coef(self, column:str, value:float):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute(f'''UPDATE coef SET {column} = ?, updated_at = ? WHERE id = 1''',
                      (value, datetime.now().strftime("%d-%m-%Y %H:%M:%S")))

            logger.info(f"Коэффициент таблицы {column} изменен. Теперь он {value}")
            conn.commit()
    def set_user_name(self, message_id, user_id=None, user_ref=None):
        if not user_id and not user_ref:
            return False
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                    INSERT INTO id_cache
                    (message_id, user_id, user_ref) 
                    VALUES (?, ?, ?)''', (message_id, user_id, user_ref))
            conn.commit()
            return True
    def get_user_name(self, message_id):
        """По message_id: удаляет строку И возвращает (message_id, user_id, user_ref)"""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT message_id, user_id, user_ref 
                FROM id_cache 
                WHERE message_id = ?
            ''', (message_id,))

            result = c.fetchone()  # Получаем строку

            if result:
                # Удаляем
                c.execute('DELETE FROM id_cache WHERE message_id = ?', (message_id,))
                conn.commit()

            return result

    def get_latest_time(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT updated_at
                         FROM currency
                         ORDER BY id DESC LIMIT 1''')
            result = c.fetchone()
            if not result:
                qdb.update_currency()
                self.get_latest_time()
            updated_at = datetime.strptime(result[0], "%d-%m-%Y %H:%M:%S.%f")
            return updated_at


if __name__ == "__main__":
   qdb = QueueDB()


   



