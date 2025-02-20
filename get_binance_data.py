import requests
import asyncio
import os
from telegram import Bot
from binance.client import Client

# Telegram Bot Credentials
TELEGRAM_TOKEN = "8146516826:AAE_y7zgsvuvYBig48Npwewga0QxNSrJ_aQ"
CHAT_ID = "1529697706"
bot = Bot(token=TELEGRAM_TOKEN)

# Binance API Credentials
BINANCE_API_KEY = "iSa2nW8ckrHQ285Y9nzlVQYV5HBvg2B70Ws74cXaspzgz13spfk9QFUderUJAV9M"
BINANCE_API_SECRET = "Yb3TOlo4vz8CRtpxkXEBwhLmzETzl2J3IZUruCOBYEAJPtdXC6Jt2dNIHKBtXr75"
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

# Fetch BTC market data from Binance
def get_btc_data(interval, limit):
    klines = client.get_klines(symbol="BTCUSDT", interval=interval, limit=limit)
    highs = [float(k[2]) for k in klines]  # High prices
    lows = [float(k[3]) for k in klines]  # Low prices

    highest_high = max(highs)
    lowest_low = min(lows)

    filtered_highs = [h for h in highs if h >= highest_high]
    filtered_lows = [l for l in lows if l <= lowest_low]

    return filtered_highs, filtered_lows


# Fetch the latest hourly BTC candle
def get_hourly_btc():
    klines = client.get_klines(symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_1HOUR, limit=1)
    last_candle = klines[-1]
    hourly_high = float(last_candle[2])
    hourly_low = float(last_candle[3])
    hourly_close = float(last_candle[4])

    return hourly_high, hourly_low, hourly_close


# Check if conditions are met and send alerts
def check_conditions():
    daily_highs, daily_lows = get_btc_data(Client.KLINE_INTERVAL_1DAY, 5)
    weekly_highs, weekly_lows = get_btc_data(Client.KLINE_INTERVAL_1WEEK, 5)
    monthly_highs, monthly_lows = get_btc_data(Client.KLINE_INTERVAL_1MONTH, 5)
    hourly_high, hourly_low, hourly_close = get_hourly_btc()

    if hourly_high is None:
        return  # Skip if data couldn't be fetched

    alert_message = "test"

    for h in daily_highs + weekly_highs + monthly_highs:
        if hourly_high > h and hourly_close < h:  # Fakeout: Breaks above but closes below
            alert_message += f"BTC Hourly fakeout above a previous high ({h})! \n"

    for l in daily_lows + weekly_lows + monthly_lows:
        if hourly_low < l and hourly_close > l:  # Fakeout: Breaks below but closes above
            alert_message += f"BTC Hourly fakeout below a previous low ({l})! \n"

    if alert_message:
        async def send_telegram_message():
            await bot.send_message(chat_id=CHAT_ID, text=alert_message)
        asyncio.run(send_telegram_message())


# Run the check every hour
if __name__ == "__main__":
    check_conditions()
