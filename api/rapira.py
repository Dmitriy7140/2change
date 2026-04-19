import requests


class RapiraAPI:
    def __init__(self, url="https://api.rapira.net/open/market/rates"):
        self.url = url

    def _fetch(self):
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_usdt_rub(self):
        data = self._fetch()

        for item in data.get("data", []):
            if item.get("symbol") == "USDT/RUB":
                return {
                    "askPrice": item.get("askPrice"),
                    "bidPrice": item.get("bidPrice"),
                }

        return None
