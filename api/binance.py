from decimal import Decimal

import requests


class BinanceAPI:
    """Reads public Binance P2P prices needed for the rates table."""

    AD_LIST_URL = "https://www.binance.com/bapi/c2c/v1/public/c2c/agent/ad-list"

    def get_second_best_usdt_gel_sell_price(self) -> Decimal | None:
        """Return the second distinct P2P price, or the only available price.

        The first several advertisements can have the same best price. We need
        the next price level, not simply the second item in Binance's response.
        If Binance returns only one distinct level, it is still a usable price.
        ``None`` means that Binance returned no prices at all.
        """
        response = requests.get(
            self.AD_LIST_URL,
            params={
                "fiat": "GEL",
                "asset": "USDT",
                "tradeType": "SELL",
                "limit": 20,
            },
            headers={"clienttype": "web"},
            timeout=10,
        )
        response.raise_for_status()

        payload = response.json()
        if not payload.get("success"):
            raise ValueError(f"Binance P2P returned an error: {payload}")

        items = payload.get("data", {}).get("items", [])
        prices = sorted(
            {Decimal(str(ad["price"])) for ad in items if "price" in ad},
            reverse=True,
        )
        if not prices:
            return None
        if len(prices) == 1:
            return prices[0]

        return prices[1]
