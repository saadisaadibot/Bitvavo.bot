import requests
import time
import hmac
import hashlib

API_KEY = "048978b32d41f1c2760696de00d61bc0d3973a1815379628fc3dd6bda9933776"
API_SECRET = "617c1100573da9820ce0f47dd4d3928c8db39251e7cc3997409711f92fff61f1a5580c1bec3db28f6eb89b523fb1b31446f394c97bab575dcc9ed876de751ab8"
BASE_URL = "https://api.bitvavo.com/v2"

def get_server_time():
    r = requests.get(BASE_URL + "/time")
    return str(r.json()["time"])

def sign_request(method, path, body=""):
    timestamp = get_server_time()
    message = timestamp + method + "/" + path + body
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return {
        "Bitvavo-Access-Key": API_KEY,
        "Bitvavo-Access-Signature": signature,
        "Bitvavo-Access-Timestamp": timestamp,
        "Bitvavo-Access-Window": "10000",
        "Content-Type": "application/json"
    }

def get_markets():
    url = BASE_URL + "/markets"
    headers = sign_request("GET", "markets")
    r = requests.get(url, headers=headers)
    return r.json()

if __name__ == "__main__":
    markets = get_markets()
    print(markets)  # ð ÙØ¹Ø±Ø¶ Ø´ÙÙ Ø§ÙØ¨ÙØ§ÙØ§Øª
    if isinstance(markets, list):
        for m in markets:
            if isinstance(m, dict) and "market" in m:
                print(m["market"])
            else:
                print("â Ø¹ÙØµØ± ØºÙØ± ÙØªÙÙØ¹:", m)
    else:
        print("â Ø§ÙØ±Ø¯ ÙÙØ³ ÙØ§Ø¦ÙØ©:", type(markets), markets)
