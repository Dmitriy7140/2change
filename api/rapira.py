import requests


class RapiraAPI:
    def __init__(self, url="https://rapira-api.pnator.ru/open/market/rates"):
        self.url = url

    def _fetch(self):
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_usdt_rub(self):
        data = self._fetch()

        return data if data else None
