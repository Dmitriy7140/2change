import requests


class KrakenAPI:
    def __init__(self, url="https://api.kraken.com/0/public/Ticker"):
        self.url = url

    def get_usdt_eur(self):
        """USDT/EUR — евро за 1 USDT. Возвращает last/bid/ask или None."""
        response = requests.get(self.url, params={"pair": "USDTEUR"}, timeout=10)
        response.raise_for_status()
        result = response.json().get("result", {})
        if not result:
            return None
        v = next(iter(result.values()))  # Kraken может вернуть ключ вида "USDTEUR"
        return {
            "last": float(v["c"][0]),
            "bid": float(v["b"][0]),
            "ask": float(v["a"][0]),
        }
