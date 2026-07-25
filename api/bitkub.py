import requests

def get_usdt_thb():

    url = "https://api.bitkub.com/api/market/ticker"
    params = {
        "sym": "USDT_THB"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    return float(data["THB_USDT"]["last"])
