import aiohttp
import asyncio
from datetime import datetime

# إعدادات تيليغرام
BOT_TOKEN = "8050663945:AAEv3uHFTsAwH_Nw6HEgMkfJWkxFhNfLoKk"
CHAT_ID = "7104122953"

# إرسال رسالة تيليغرام
async def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    async with aiohttp.ClientSession() as session:
        await session.post(url, json=payload)

# جلب أفضل 150 عملة USDT من حيث الحجم
async def get_top_usdt_symbols():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
    usdt_pairs = []
    for item in data:
        symbol = item.get('symbol', '')
        if symbol.endswith('USDT') and not symbol.endswith('BUSD'):
            usdt_pairs.append(item)
    sorted_pairs = sorted(usdt_pairs, key=lambda x: -float(x['quoteVolume']))
    return [pair['symbol'] for pair in sorted_pairs[:150]]

# المتابعة اللحظية لكل عملة
symbol_data = {}

async def analyze_symbol(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    res = await resp.json()
            price = float(res['price'])
            now = datetime.utcnow()

            if symbol not in symbol_data:
                symbol_data[symbol] = {"start_time": now, "start_price": price}
            else:
                start = symbol_data[symbol]["start_time"]
                old_price = symbol_data[symbol]["start_price"]
                diff = ((price - old_price) / old_price) * 100
                elapsed = (now - start).total_seconds()

                if 15 <= elapsed <= 20 and 1 <= diff < 3:
                    await send_telegram_message(f"🚨 حركة غير عادية في {symbol} 📈")
                    symbol_data[symbol] = {"start_time": now, "start_price": price}

                elif elapsed <= 60 and diff >= 3:
                    await send_telegram_message(f"🎯 تم قنص عملة {symbol} 💥")
                    symbol_data[symbol] = {"start_time": now, "start_price": price}

            await asyncio.sleep(15)

        except Exception as e:
            print(f"❌ خطأ في {symbol}: {e}")
            await asyncio.sleep(5)

# تشغيل الكل
async def main():
    await send_telegram_message("✅ تم تشغيل بوت صقر لتحليل السوق 🔍")
    symbols = await get_top_usdt_symbols()
    tasks = [analyze_symbol(symbol) for symbol in symbols]
    await asyncio.gather(*tasks)

# بداية البرنامج
if __name__ == "__main__":
    asyncio.run(main())
