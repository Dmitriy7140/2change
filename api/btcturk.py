import requests

def get_usdt_try():
    url = "https://api.btcturk.com/api/v2/ticker?pairSymbol=USDTTRY"
    response = requests.get(url).json()
    return float(response["data"][0]["last"])

