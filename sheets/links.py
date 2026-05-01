import time
import gspread
from utils import logger
from database_users import UserDB



class AnalSheets:
    def __init__(self, userdb: UserDB):
        self.gc = gspread.service_account(filename="sheets/creds.json")
        self.ws = self.gc.open("2change_analysis").worksheet("links")
        self.userdb=userdb

    def sync_links(self):
        try:
            db_rows = self.userdb.get_links()

            sheet_data = self.ws.get_all_values()[1:]

            link_to_row = {}
            for i, row in enumerate(sheet_data, start=2):
                if row and row[0]:
                    link_to_row[row[0]] = i

            new_rows = []

            for r in db_rows:
                link = r["link"]
                followed = r["followed"]

                if link in link_to_row:
                    row_num = link_to_row[link]
                    self.ws.update(f"B{row_num}", [[followed]])
                else:
                    new_rows.append([link, followed])

            if new_rows:
                self.ws.append_rows(new_rows, value_input_option="RAW")

            logger.info(f"Синхронизировали: {len(db_rows)} записей")

        except Exception as e:
            logger.error(f"Ошибка синхронизации: {e}")


def anal_loop(anal_sheets: AnalSheets):
    while True:
        try:
            anal_sheets.sync_links()
        except Exception as e:
            logger.error(f"Loop error: {e}")

        time.sleep(1800)