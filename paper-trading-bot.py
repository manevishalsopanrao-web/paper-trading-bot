# =========================================================
# AWS LIVE PAPER TRADING BOT + WHATSAPP ALERT (TWILIO)
# ✅ Runs 24x7 on AWS EC2
# ✅ Trades ONLY during market hours (09:15 AM to 03:30 PM IST)
# ✅ Asia/Kolkata Timezone Fixed
# ✅ Trailing Stop Loss
# ✅ One Trade Per Stock Per Day
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
# TIMEZONE (INDIA)
# =========================================================
IST = ZoneInfo("Asia/Kolkata")

# =========================================================
# TWILIO SETUP
# =========================================================
account_sid = "AC39a3d89a71a3d05de1928c42a8e23754"
auth_token = "95190c0106d0e29b6c17a3295b4e7622"   # ⚠️ तुमचा खरा Auth Token टाका

client = Client(account_sid, auth_token)

YOUR_WHATSAPP = "whatsapp:+918888135316"
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
# FULL STOCK LIST (UNCHANGED)
# =========================================================
stocks = [
    "RELIANCE","HDFCBANK","ICICIBANK","SBIN","KOTAKBANK","AXISBANK",
    "BAJFINANCE","BAJAJFINSV","CHOLAFIN","SHRIRAMFIN","LICHSGFIN",
    "AUBANK","MUTHOOTFIN","INFY","TCS","HCLTECH","TECHM",
    "PERSISTENT","COFORGE","MPHASIS","TATAELXSI","LTTS",
    "SONATSOFTW","INTELLECT","BSOFT","KPITTECH",

    "SUNPHARMA","CIPLA","DRREDDY","TORNTPHARM","LUPIN",
    "AUROPHARMA","GLAND","AJANTPHARM","MANKIND","MEDANTA",
    "MAXHEALTH","FORTIS","RAINBOW","KIMS",

    "M&M","HEROMOTOCO","TVSMOTOR","BHARATFORG","BALKRISIND",

    "SIEMENS","CUMMINSIND","KEI","HAVELLS",
    "VOLTAS","BLUESTARCO","THERMAX","SCHNEIDER",

    "LT","GRASIM","PIDILITIND","ASTRAL",
    "APLAPOLLO","DALBHARAT","JKCEMENT","KAJARIACER",

    "TITAN","TRENT","DMART","BRITANNIA","NESTLEIND",
    "HINDUNILVR","MARICO","COLPAL",

    "ADANIENT","ADANIPORTS","HAL","BEL","BDL","MCX",
    "CDSL","CAMS","NAUKRI","INDIAMART","POLICYBZR",

    "TORNTPOWER","JSWENERGY","CGPOWER",
    "TATACOMM","INDIGO","OBEROIRLTY","PHOENIXLTD",

    "GRWRHITECH","PFIZER","SUNDARMFIN","FINEORG","BAYERCROP",
    "INGERRAND","NETWEB","KAYNES","ORISSAMINE","SCHAEFFLER",
    "DATAPATTNS","CRISIL","AIAENG","BSE",
    "FLUOROCHEM","BASF","ANANDRATHI","TIMKEN","SANOFI",
    "CEATLTD","RADICO","GRSE","PRUDENT","BBL","RATNAMANI",
    "MAZDOCK","POWERMECH","TIIL","SANSERA","GLAXO",
    "ETHOSLTD","DOMS","ENDURANCE","STYLAMIND","GODFRYPHLP",
    "FIEMIND","AZAD","JBCHEPHARM","BEML","CAPLIPOINT",
    "CARTRADE","RRKABEL","GRAVITA","LLOYDSME","ALKYLAMINE",
    "COCHINSHIP","KIRLOSBROS","WOCKPHARMA","NEOGEN",
    "SKFINDIA","MASTEK","EMCURE","POLYMED","TEGA",
    "GRINDWELL","VENKEYS","ECLERX","ZENTEC","KIRLPNU",
    "BBTC","ABREL","BHARTIHEXA","INOXINDIA","WABAG",
    "BALAMINES","SAFARI","VEEDOL","SOBHA","AFFLE",
    "LUXIND","AAVAS","NUVAMA","VENUSPIPES","VINATIORGA",
    "ERIS","EPIGRAL","TEAMLEASE","DEEPAKFERT",
    "DCMSHRIRAM","TECHNOE","KPIL","NESCO","CIGNITITEC",
    "OLECTRA","TBOTEK","HOMEFIRST","CONCORDBIO",
    "ENTERO","VIJAYA"
]

# =========================================================
# SETTINGS
# =========================================================
SPIKE_THRESHOLD = 8
RSI_LEVEL = 60

INITIAL_SL_PCT = 0.02      # Initial Stop Loss = 2%
TRAILING_SL_PCT = 0.02     # Trailing Stop Loss = 2%

START_CAPITAL = 100000
CAPITAL = START_CAPITAL

MAX_DAILY_LOSS = 5000
DAILY_PNL = 0
TRADING_DISABLED = False

# Market Timings (IST)
MARKET_START = dtime(9, 15)
MARKET_END = dtime(15, 30)

# Sleep intervals (seconds)
CLOSED_SLEEP = 300   # 5 minutes
OPEN_SLEEP = 300     # 5 minutes

# =========================================================
# ONE TRADE PER STOCK PER DAY
# =========================================================
traded_today = set()
current_trade_date = datetime.now(IST).date()

# =========================================================
# GET CURRENT IST TIME
# =========================================================
def now_ist():
    return datetime.now(IST)

# =========================================================
# RESET DAILY DATA
# =========================================================
def reset_daily_data():
    global traded_today, DAILY_PNL, TRADING_DISABLED, current_trade_date

    today = now_ist().date()

    if today != current_trade_date:
        traded_today = set()
        DAILY_PNL = 0
        TRADING_DISABLED = False
        current_trade_date = today

        print("🔄 New Trading Day Reset")

        send_whatsapp(
            f"🌅 New Trading Day Started\n"
            f"Date: {today}\n"
            f"Capital: {CAPITAL:.2f}"
        )

# =========================================================
# CHECK MARKET OPEN (IST)
# =========================================================
def market_open():
    now = now_ist()

    # Stop if daily loss hit
    if TRADING_DISABLED:
        return False

    # Weekend check (Saturday=5, Sunday=6)
    if now.weekday() > 4:
        return False

    # Time check
    current_time = now.time()
    if current_time < MARKET_START or current_time >= MARKET_END:
        return False

    return True

# =========================================================
# RUN BOT
# =========================================================
def run_bot():
    global CAPITAL, DAILY_PNL, TRADING_DISABLED

    for stock in stocks:
        try:
            # Skip if already traded today
            if stock in traded_today:
                continue

            # Download latest 5-minute data
            data = yf.Ticker(stock + ".NS").history(
                period="5d",
                interval="5m",
                auto_adjust=True
            )

            if data.empty or len(data) < 200:
                continue

            # Indicators
            data["EMA9"] = data["Close"].ewm(span=9).mean()
            data["EMA15"] = data["Close"].ewm(span=15).mean()
            data["EMA21"] = data["Close"].ewm(span=21).mean()
            data["RSI"] = ta.momentum.RSIIndicator(data["Close"]).rsi()

            # Entry Scan
            for i in range(200, len(data) - 2):

                vol = data["Volume"].iloc[i]
                avg_vol = data["Volume"].iloc[i-20:i].mean()

                if avg_vol == 0:
                    continue

                # Volume Spike
                if vol / avg_vol < SPIKE_THRESHOLD:
                    continue

                # RSI Filter
                rsi = data["RSI"].iloc[i]
                if pd.isna(rsi) or rsi < RSI_LEVEL:
                    continue

                # Entry
                entry_price = data["Open"].iloc[i + 1]
                entry_time = data.index[i + 1]

                # Quantity
                qty = int(CAPITAL / entry_price)
                if qty <= 0:
                    continue

                # Initial Stop Loss
                highest_price = entry_price
                trailing_stop = entry_price * (1 - INITIAL_SL_PCT)

                # Default Exit
                exit_price = entry_price
                exit_time = entry_time
                reason = "MARKET CLOSE"

                # Exit Logic
                for j in range(i + 2, len(data)):

                    current_price = data["Close"].iloc[j]

                    # Update trailing stop
                    if current_price > highest_price:
                        highest_price = current_price
                        trailing_stop = highest_price * (1 - TRAILING_SL_PCT)

                    # Trailing Stop Loss
                    if current_price <= trailing_stop:
                        exit_price = current_price
                        exit_time = data.index[j]
                        reason = "TRAILING STOPLOSS"
                        break

                    # EMA Exit
                    if current_price < data["EMA9"].iloc[j]:
                        exit_price = current_price
                        exit_time = data.index[j]
                        reason = "EMA EXIT"
                        break

                    # Last candle exit
                    exit_price = current_price
                    exit_time = data.index[j]

                # P&L
                pnl = (exit_price - entry_price) * qty

                CAPITAL += pnl
                DAILY_PNL += pnl

                # Mark stock traded
                traded_today.add(stock)

                # Console Output
                print("=" * 60)
                print(f"📈 STOCK        : {stock}")
                print(f"🕒 ENTRY TIME   : {entry_time}")
                print(f"🕒 EXIT TIME    : {exit_time}")
                print(f"💵 ENTRY PRICE  : {entry_price:.2f}")
                print(f"💵 EXIT PRICE   : {exit_price:.2f}")
                print(f"📦 QTY          : {qty}")
                print(f"📌 REASON       : {reason}")
                print(f"💰 PNL          : {pnl:.2f}")
                print(f"📉 DAILY PNL    : {DAILY_PNL:.2f}")
                print(f"💼 CAPITAL      : {CAPITAL:.2f}")
                print("=" * 60)

                # WhatsApp Alert
                send_whatsapp(
                    f"📊 TRADE ALERT\n"
                    f"Stock: {stock}\n"
                    f"Entry: {entry_price:.2f}\n"
                    f"Exit: {exit_price:.2f}\n"
                    f"Qty: {qty}\n"
                    f"PnL: {pnl:.2f}\n"
                    f"Daily PnL: {DAILY_PNL:.2f}\n"
                    f"Reason: {reason}\n"
                    f"Capital: {CAPITAL:.2f}"
                )

                # Daily Loss Protection
                if DAILY_PNL <= -MAX_DAILY_LOSS:
                    TRADING_DISABLED = True

                    print("⛔ BOT STOPPED DUE TO DAILY LOSS LIMIT")

                    send_whatsapp(
                        f"🚨 BOT STOPPED\n"
                        f"Daily Loss Limit Hit\n"
                        f"Daily PnL: {DAILY_PNL:.2f}"
                    )
                    return

                # Only one trade per stock per day
                break

        except Exception as e:
            print("❌ Error:", stock, e)

# =========================================================
# MAIN LOOP - RUNS 24x7
# =========================================================
print("🚀 BOT STARTED (24x7 Mode)")
print("📈 Trades only during market hours")
print("🕘 Market Time: 09:15 AM to 03:30 PM IST")
print(f"🌏 Timezone: {IST}")

send_whatsapp("🚀 Paper Trading Bot Started on AWS (24x7 Mode, Asia/Kolkata)")

while True:
    try:
        # Reset every new day
        reset_daily_data()

        current_time = now_ist()

        if market_open():
            print(f"\n🔥 MARKET OPEN - {current_time}")
            run_bot()

            print(f"💼 CAPITAL      : {CAPITAL:.2f}")
            print(f"📉 DAILY PNL    : {DAILY_PNL:.2f}")
            print(f"📌 TRADED TODAY : {len(traded_today)} stocks")

            # Scan every 5 minutes
            time.sleep(OPEN_SLEEP)

        else:
            print(f"⏳ MARKET CLOSED - {current_time}")

            # Sleep 5 minutes and check again
            time.sleep(CLOSED_SLEEP)

    except Exception as e:
        print("❌ MAIN LOOP ERROR:", e)

        send_whatsapp(f"⚠️ Bot Error: {e}")

        # Wait 1 minute and continue
        time.sleep(60)
