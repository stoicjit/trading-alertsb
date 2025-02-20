import requests
import asyncio
from flask import Flask, request, jsonify
from telegram import Bot

# Flask app for receiving TradingView webhooks
app = Flask(__name__)

# Telegram Bot Credentials
TELEGRAM_TOKEN = "8146516826:AAE_y7zgsvuvYBig48Npwewga0QxNSrJ_aQ"
CHAT_ID = "1529697706"
bot = Bot(token=TELEGRAM_TOKEN)

# Store previous highs and lows
daily_highs, daily_lows = [], []
weekly_highs, weekly_lows = [], []
monthly_highs, monthly_lows = [], []


# Webhook route to receive TradingView alerts
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    timeframe = data.get("timeframe")
    high = float(data.get("high"))
    low = float(data.get("low"))
    close = float(data.get("close"))

    if timeframe == "1D":
        daily_highs.append(high)
        daily_lows.append(low)
    elif timeframe == "1W":
        weekly_highs.append(high)
        weekly_lows.append(low)
    elif timeframe == "1M":
        monthly_highs.append(high)
        monthly_lows.append(low)

    check_conditions(high, low, close)
    return jsonify({"message": "Webhook received"}), 200


# Check for fakeouts
def check_conditions(hourly_high, hourly_low, hourly_close):
    alert_message = ""

    for h in daily_highs + weekly_highs + monthly_highs:
        if hourly_high > h and hourly_close < h:
            alert_message += f"BTC Hourly fakeout above a previous high ({h})! \n"

    for l in daily_lows + weekly_lows + monthly_lows:
        if hourly_low < l and hourly_close > l:
            alert_message += f"BTC Hourly fakeout below a previous low ({l})! \n"

    if alert_message:
        async def send_telegram_message():
            await bot.send_message(chat_id=CHAT_ID, text=alert_message)
        asyncio.run(send_telegram_message())


# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
