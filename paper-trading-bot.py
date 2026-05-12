# =========================================================
# AWS LIVE PAPER TRADING BOT + WHATSAPP ALERT (TWILIO)
# ✅ Runs 24x7 on AWS EC2
# ✅ Trades ONLY during Indian Market Hours (IST)
# ✅ Timezone Fixed to Asia/Kolkata
# =========================================================

import yfinance as yf
import ta
import pandas as pd
import warnings
import time
from datetime import datetime, time as dtime, date
from zoneinfo import ZoneInfo
from twilio.rest import Client

warnings.filterwarnings("ignore")

# =========================================================
# INDIA TIMEZONE (IMPORTANT FIX)
# =========================================================
IST = ZoneInfo("Asia/Kolkata")

# =========================================================
# TWILIO SETUP
# =========================================================
account_sid = "YOUR_ACCOUNT_SID"
auth_token = "YOUR_AUTH_TOKEN"

client = Client(account_sid, auth_token)

YOUR_WHATSAPP = "whatsapp:+91XXXXXXXXXX"
TWILIO_NUMBER = "whatsapp:+14155238886"

def send_whatsapp(msg):
    try:
        client.messages.create(
            from_=TWILIO_NUMBER,
            to=YOUR_WHATSAPP,
            body=msg
        )
        print("📲 WhatsApp Sent")
    except Exception as e:
        print("❌ WhatsApp Error:", e)

# =========================================================
# SETTINGS
# =========================================================
START_CAPITAL = 100000
CAPITAL = START_CAPITAL

MAX_DAILY_LOSS = 5000
DAILY_PNL = 0
TRADING_DISABLED = False

# Indian Market Timings (IST)
MARKET_START = dtime(9, 15)
MARKET_END = dtime(15, 30)

# Sleep timings
CLOSED_SLEEP = 300   # 5 minutes
OPEN_SLEEP = 300     # 5 minutes

# =========================================================
# TRADE TRACKING
# =========================================================
traded_today = set()
current_trade_date = datetime.now(IST).date()

# =========================================================
# RESET DAILY DATA
# =========================================================
def reset_daily_data():
    global traded_today, DAILY_PNL, TRADING_DISABLED, current_trade_date

    today = datetime.now(IST).date()

    if today != current_trade_date:
        traded_today = set()
        DAILY_PNL = 0
        TRADING_DISABLED = False
        current_trade_date = today

        print("🔄 New Trading Day Reset")

        send_whatsapp(
            f"🌅 New Trading Day Started\n"
            f"Capital: {CAPITAL:.2f}"
        )

# =========================================================
# CHECK MARKET OPEN (IST TIMEZONE FIXED)
# =========================================================
def market_open():
    global TRADING_DISABLED

    # Current Indian Standard Time
    now = datetime.now(IST)

    print(f"🇮🇳 Current IST Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    # Stop if daily loss limit hit
    if TRADING_DISABLED:
        print("⛔ Trading Disabled Due To Daily Loss Limit")
        return False

    # Weekend check
    # Monday = 0, Tuesday = 1, ..., Saturday = 5, Sunday = 6
    if now.weekday() > 4:
        print("📅 Weekend - Market Closed")
        return False

    # Remove timezone info from time object for comparison
    current_time = now.time().replace(tzinfo=None)

    # Before market open
    if current_time < MARKET_START:
        print("⏰ Before 09:15 AM IST - Market Closed")
        return False

    # After market close
    if current_time >= MARKET_END:
        print("⏰ After 03:30 PM IST - Market Closed")
        return False

    print("🔥 Market is OPEN")
    return True

# =========================================================
# DUMMY BOT FUNCTION
# (Replace with your full trading logic)
# =========================================================
def run_bot():
    global CAPITAL, DAILY_PNL

    print("📈 Running Paper Trading Strategy...")
    print(f"💼 Current Capital: {CAPITAL:.2f}")
    print(f"📉 Daily PnL: {DAILY_PNL:.2f}")

# =========================================================
# MAIN LOOP - RUNS 24x7
# =========================================================
print("🚀 BOT STARTED (24x7 Mode)")
print("📈 Trades only during market hours")
print("🕘 Market Time: 09:15 AM to 03:30 PM IST")
print("🌍 Timezone: Asia/Kolkata")

send_whatsapp("🚀 Paper Trading Bot Started on AWS (Asia/Kolkata Timezone Fixed)")

while True:
    try:
        # Reset every new trading day using IST
        reset_daily_data()

        # Check if Indian market is open
        if market_open():
            print(f"\n🔥 MARKET OPEN - {datetime.now(IST)}")

            # Run trading logic
            run_bot()

            print(f"💼 CAPITAL      : {CAPITAL:.2f}")
            print(f"📉 DAILY PNL    : {DAILY_PNL:.2f}")
            print(f"📌 TRADED TODAY : {len(traded_today)} stocks")

            # Wait 5 minutes before next scan
            time.sleep(OPEN_SLEEP)

        else:
            print(f"⏳ MARKET CLOSED - {datetime.now(IST)}")

            # Wait 5 minutes and check again
            time.sleep(CLOSED_SLEEP)

    except Exception as e:
        print("❌ MAIN LOOP ERROR:", e)

        send_whatsapp(f"⚠️ Bot Error: {e}")

        # Wait 1 minute and continue
        time.sleep(60)
