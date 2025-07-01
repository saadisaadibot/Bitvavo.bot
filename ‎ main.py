
import time
import hmac
import hashlib
import base64
import requests
import json
from datetime import datetime

API_KEY = '048978b32d41f1c2760696de00d61bc0d3973a1815379628fc3dd6bda9933776'
API_SECRET = '617c1100573da9820ce0f47dd4d3928c8db39251e7cc3997409711f92fff61f1a5580c1bec3db28f6eb89b523fb1b31446f394c97bab575dcc9ed876de751ab8'

BASE_URL = 'https://api.bitvavo.com/v2'

def get_timestamp():
    return str(int(time.time() * 1000))

def sign_request(method, path, body, timestamp):
    body_str = json.dumps(body) if body else ''
    pre_sign = timestamp + method + path + body_str
    signature = hmac.new(base64.b64decode(API_SECRET), pre_sign.encode('utf-8'), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()

def authenticated_request(method, path, body=None):
    timestamp = get_timestamp()
    signature = sign_request(method, path, body, timestamp)
    headers = {
        'Bitvavo-Access-Key': API_KEY,
        'Bitvavo-Access-Timestamp': timestamp,
        'Bitvavo-Access-Signature': signature,
        'Content-Type': 'application/json'
    }
    url = BASE_URL + path
    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'POST':
        response = requests.post(url, headers=headers, data=json.dumps(body))
    else:
        raise ValueError("Unsupported HTTP method")
    return response.json()

def get_all_markets():
    return authenticated_request('GET', '/markets')

def get_price(market):
    data = authenticated_request('GET', f'/ticker/price?market={market}')
    return float(data['price']) if 'price' in data else None

def place_order(market, amount, price=None, side='buy'):
    order = {
        'market': market,
        'side': side,
        'orderType': 'market' if price is None else 'limit',
        'amount': str(amount)
    }
    if price:
        order['price'] = str(price)
    return authenticated_request('POST', '/order', order)

def run_bot():
    print("Starting Bitvavo trading bot...")
    while True:
        try:
            markets = get_all_markets()
            for market in markets:
                if not market['market'].endswith('-EUR'):
                    continue
                price = get_price(market['market'])
                if price and price > 10:
                    print(f"{datetime.now()} - Buying 10€ of {market['market']} at price {price}")
                    result = place_order(market['market'], 10 / price)
                    print("Order result:", result)
            time.sleep(60)
        except Exception as e:
            print("Error:", e)
            time.sleep(60)

if __name__ == '__main__':
    run_bot()
