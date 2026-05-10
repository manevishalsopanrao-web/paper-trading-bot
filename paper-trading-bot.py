# =========================================================
# AWS LIVE PAPER TRADING BOT + WHATSAPP ALERT (TWILIO)
# ✅ Trailing Stop Loss Added
# ✅ One Trade Per Stock Per Day
# =========================================================

import yfinance as yf
import ta
import pandas as pd
import warnings
import time
from datetime import datetime, time as dtime, date
from twilio.rest import Client

warnings.filterwarnings("ignore")

# =========================================================
# TWILIO SETUP
# =========================================================
account_sid = "AC39a3d89a71a3d05de1928c42a8e23754"
auth_token = "6f65d9eb89992cfa3f5eb80465c28a2b"

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
# FULL STOCK LIST
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

    "M&M","HEROMOTOCO",
    "TVSMOTOR","BHARATFORG","BALKRISIND",

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
    "DATAPATTNS","CRISIL","THERMAX","AIAENG","BSE",
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

MARKET_START = dtime(9, 15)
MARKET_END = dtime(15, 30)

# =========================================================
# ONE TRADE PER STOCK PER DAY
# =========================================================
traded_today = set()
current_trade_date = date.today()

# =========================================================
def reset_daily_data():
    global traded_today, DAILY_PNL, TRADING_DISABLED, current_trade_date

    today = date.today()

    if today != current_trade_date:
        traded_today = set()
        DAILY_PNL = 0
        TRADING_DISABLED = False
        current_trade_date = today
        print("🔄 New Trading Day Reset")

# =========================================================
def market_open():
    now = datetime.now()

    if TRADING_DISABLED:
        return False

    if now.weekday() > 4:  # Saturday/Sunday
        return False

    if now.time() < MARKET_START or now.time() >= MARKET_END:
        return False

    return True

# =========================================================
def run_bot():
    global CAPITAL, DAILY_PNL, TRADING_DISABLED

    for stock in stocks:
        try:
            # -------------------------------------------------
            # Skip if already traded today
            # -------------------------------------------------
            if stock in traded_today:
                continue

            # -------------------------------------------------
            # Download Data
            # -------------------------------------------------
            data = yf.Ticker(stock + ".NS").history(period="5d", interval="5m")

            if data.empty or len(data) < 200:
                continue

            # -------------------------------------------------
            # Indicators
            # -------------------------------------------------
            data["EMA9"] = data["Close"].ewm(span=9).mean()
            data["EMA15"] = data["Close"].ewm(span=15).mean()
            data["EMA21"] = data["Close"].ewm(span=21).mean()
            data["RSI"] = ta.momentum.RSIIndicator(data["Close"]).rsi()

            # -------------------------------------------------
            # Find Entry
            # -------------------------------------------------
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

                # =====================================================
                # INITIAL STOP LOSS
                # =====================================================
                highest_price = entry_price
                trailing_stop = entry_price * (1 - INITIAL_SL_PCT)

                exit_price = entry_price
                exit_time = entry_time
                reason = "MARKET CLOSE"

                # =====================================================
                # EXIT LOGIC WITH TRAILING STOP LOSS
                # =====================================================
                for j in range(i + 2, len(data)):

                    current_price = data["Close"].iloc[j]

                    # Update highest price
                    if current_price > highest_price:
                        highest_price = current_price
                        trailing_stop = highest_price * (1 - TRAILING_SL_PCT)

                    # Trailing Stop Loss Hit
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

                    # If no exit, close at last candle
                    exit_price = current_price
                    exit_time = data.index[j]

                # =====================================================
                # P&L Calculation
                # =====================================================
                pnl = (exit_price - entry_price) * qty

                CAPITAL += pnl
                DAILY_PNL += pnl

                # Mark stock as traded today
                traded_today.add(stock)

                # =====================================================
                # Print Output
                # =====================================================
                print("=" * 60)
                print(f"📈 STOCK        : {stock}")
                print(f"🕒 ENTRY TIME   : {entry_time}")
                print(f"💵 ENTRY PRICE  : {entry_price:.2f}")
                print(f"💵 EXIT PRICE   : {exit_price:.2f}")
                print(f"📦 QTY          : {qty}")
                print(f"📌 REASON       : {reason}")
                print(f"💰 PNL          : {pnl:.2f}")
                print(f"💼 CAPITAL      : {CAPITAL:.2f}")
                print("=" * 60)

                # =====================================================
                # WhatsApp Alert
                # =====================================================
                send_whatsapp(
                    f"📊 TRADE ALERT\n"
                    f"Stock: {stock}\n"
                    f"Entry: {entry_price:.2f}\n"
                    f"Exit: {exit_price:.2f}\n"
                    f"Qty: {qty}\n"
                    f"PnL: {pnl:.2f}\n"
                    f"Reason: {reason}\n"
                    f"Capital: {CAPITAL:.2f}"
                )

                # =====================================================
                # Daily Loss Protection
                # =====================================================
                if DAILY_PNL <= -MAX_DAILY_LOSS:
                    TRADING_DISABLED = True

                    send_whatsapp(
                        f"🚨 BOT STOPPED\n"
                        f"Daily Loss Hit: {DAILY_PNL:.2f}"
                    )

                    print("⛔ BOT STOPPED DUE TO DAILY LOSS LIMIT")
                    return

                # One trade per stock per day → stop scanning this stock
                break

        except Exception as e:
            print("❌ Error:", stock, e)

# =========================================================
# MAIN LOOP
# =========================================================
print("🚀 BOT STARTED WITH TRAILING STOP LOSS + ONE TRADE PER STOCK PER DAY")

while True:
    # Reset at new day
    reset_daily_data()

    if market_open():
        print("\n🔥 MARKET OPEN")
        run_bot()
        print(f"💰 CAPITAL: {CAPITAL:.2f}")
        print(f"📉 DAILY PNL: {DAILY_PNL:.2f}")
        print(f"📌 TRADED TODAY: {len(traded_today)} stocks")
        time.sleep(300)   # 5 minutes

    else:
        print("⏳ MARKET CLOSED")
        time.sleep(300)
