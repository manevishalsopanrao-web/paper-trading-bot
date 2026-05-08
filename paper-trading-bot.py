import yfinance as yf
import ta
import pandas as pd
import warnings
import time
from datetime import datetime, time as dtime

warnings.filterwarnings("ignore")

# =========================================================
# FULL STOCK LIST (YOUR ORIGINAL)
# =========================================================
stocks = [
    "GRWRHITECH","PFIZER","SUNDARMFIN","FINEORG","BAYERCROP",
    "INGERRAND","NETWEB","KAYNES","ORISSAMINE","SCHAEFFLER",
    "DATAPATTNS","CRISIL","THERMAX","LT","AIAENG","BSE",
    "FLUOROCHEM","BASF","ANANDRATHI","TIMKEN","SANOFI",
    "CEATLTD","RADICO","M&M","AJANTPHARM","GRSE","MCX",
    "PRUDENT","BBL","RATNAMANI","MAZDOCK","POWERMECH",
    "TIIL","SANSERA","GLAXO","ETHOSLTD","DOMS","MANKIND",
    "ENDURANCE","STYLAMIND","GODFRYPHLP","FIEMIND","AZAD",
    "JBCHEPHARM","BEML","CAPLIPOINT","PHOENIXLTD","CARTRADE",
    "BLUESTARCO","GLAND","RRKABEL","GRAVITA","LLOYDSME",
    "ALKYLAMINE","COCHINSHIP","KIRLOSBROS","TORNTPOWER",
    "CHOLAHLDNG","WOCKPHARMA","NEOGEN","SKFINDIA","MASTEK",
    "EMCURE","POLYMED","TEGA","GRINDWELL","VENKEYS",
    "ECLERX","ZENTEC","KIRLPNU","BBTC","ABREL","BHARTIHEXA",
    "INOXINDIA","WABAG","BALAMINES","SAFARI","VEEDOL",
    "SOBHA","AFFLE","LUXIND","AAVAS","NUVAMA","VENUSPIPES",
    "BDL","VINATIORGA","ERIS","EPIGRAL","TEAMLEASE",
    "DEEPAKFERT","DCMSHRIRAM","TECHNOE","RAINBOW","KPIL",
    "NESCO","CIGNITITEC","OLECTRA","TBOTEK","HOMEFIRST",
    "CONCORDBIO","ENTERO","VIJAYA","MEDANTA"
]

# =========================================================
# SETTINGS
# =========================================================
SPIKE_THRESHOLD = 8
RSI_LEVEL = 60
SL_PCT = 0.02

START_CAPITAL = 100000
CAPITAL = START_CAPITAL

trades = []
last_exit_time = None

START_TIME = dtime(9, 20)
EXIT_TIME = dtime(15, 0)

# =========================================================
# MARKET TIME CHECK
# =========================================================
def market_open():
    now = datetime.now()

    # Monday-Friday only
    if now.weekday() > 4:
        return False

    # time filter
    if now.time() < START_TIME or now.time() >= EXIT_TIME:
        return False

    return True

# =========================================================
# CORE STRATEGY
# =========================================================
def run_bot():

    global CAPITAL, last_exit_time, trades

    for stock in stocks:

        try:
            data = yf.Ticker(stock + ".NS").history(period="5d", interval="5m")

            if data.empty or len(data) < 200:
                continue

            # EMA
            data["EMA9"] = data["Close"].ewm(span=9).mean()
            data["EMA15"] = data["Close"].ewm(span=15).mean()
            data["EMA21"] = data["Close"].ewm(span=21).mean()
            data["EMA50"] = data["Close"].ewm(span=50).mean()
            data["EMA100"] = data["Close"].ewm(span=100).mean()
            data["EMA200"] = data["Close"].ewm(span=200).mean()

            # RSI
            data["RSI"] = ta.momentum.RSIIndicator(data["Close"]).rsi()

            for i in range(200, len(data)-2):

                candle_time = data.index[i]

                if last_exit_time and candle_time <= last_exit_time:
                    continue

                # volume spike
                vol = data["Volume"].iloc[i]
                avg_vol = data["Volume"].iloc[i-20:i].mean()

                if avg_vol == 0:
                    continue

                spike = vol / avg_vol

                if spike < SPIKE_THRESHOLD:
                    continue

                close = data["Close"].iloc[i]
                open_price = data["Open"].iloc[i]
                rsi = data["RSI"].iloc[i]

                if pd.isna(rsi):
                    continue

                e9 = data["EMA9"].iloc[i]
                e15 = data["EMA15"].iloc[i]
                e21 = data["EMA21"].iloc[i]
                e50 = data["EMA50"].iloc[i]
                e100 = data["EMA100"].iloc[i]
                e200 = data["EMA200"].iloc[i]

                # BUY CONDITION
                if not (
                    rsi > RSI_LEVEL and
                    close > e9 > e15 > e21 > e50 > e100 > e200 and
                    close > open_price
                ):
                    continue

                entry_price = data["Open"].iloc[i+1]
                entry_time = data.index[i+1]

                qty = int(CAPITAL / entry_price)

                if qty <= 0:
                    continue

                exit_price = entry_price
                exit_time = entry_time
                reason = "HOLD"

                # EXIT LOOP
                for j in range(i+2, len(data)):

                    price = data["Close"].iloc[j]
                    t = data.index[j].time()

                    if t >= EXIT_TIME:
                        exit_price = price
                        exit_time = data.index[j]
                        reason = "3PM EXIT"
                        break

                    if price <= entry_price * (1 - SL_PCT):
                        exit_price = price
                        exit_time = data.index[j]
                        reason = "STOPLOSS"
                        break

                    if price < data["EMA9"].iloc[j]:
                        exit_price = price
                        exit_time = data.index[j]
                        reason = "EMA EXIT"
                        break

                pnl = (exit_price - entry_price) * qty
                CAPITAL += pnl

                trades.append([stock, entry_time, exit_time, pnl, reason])

                last_exit_time = exit_time

        except Exception as e:
            print("Error:", stock, e)

# =========================================================
# LIVE ENGINE (MON–FRI LOOP)
# =========================================================
while True:

    if market_open():

        print("\n🔥 MARKET OPEN - RUNNING BOT")

        run_bot()

        print("💰 CAPITAL:", round(CAPITAL, 2))
        print("📊 TOTAL TRADES:", len(trades))

    else:

        print("⏳ MARKET CLOSED")

    time.sleep(300)
