import yfinance as yf
import ta
import pandas as pd
import warnings
from datetime import time

warnings.filterwarnings("ignore")

# =========================================================
# STOCK LIST
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

SPIKE_THRESHOLD = 8      # 8X SPIKE
RSI_LEVEL = 60           # RSI 60
SL_PCT = 0.02            # 2% STOPLOSS

START_CAPITAL = 100000
CAPITAL = START_CAPITAL

# MARKET TIME
START_TIME = time(9, 20)
EXIT_TIME = time(15, 0)

# STORE TRADES
trades = []

# ONLY ONE ACTIVE TRADE
last_exit_time = None

# =========================================================
# MAIN LOOP
# =========================================================

for stock in stocks:

    try:

        # =================================================
        # DOWNLOAD DATA
        # =================================================

        data = yf.Ticker(stock + ".NS").history(

            period="5d",
            interval="5m"

        )

        if data.empty or len(data) < 250:
            continue

        # =================================================
        # EMA
        # =================================================

        for ema in [9, 15, 21, 50, 100, 200]:

            data[f"EMA{ema}"] = (

                data["Close"]
                .ewm(span=ema, adjust=False)
                .mean()

            )

        # =================================================
        # RSI
        # =================================================

        data["RSI"] = ta.momentum.RSIIndicator(

            data["Close"]

        ).rsi()

        # =================================================
        # CANDLE LOOP
        # =================================================

        for i in range(200, len(data)-2):

            candle_time = data.index[i]

            current_time = candle_time.time()

            # =============================================
            # ONLY 9:20 TO 3:00
            # =============================================

            if current_time < START_TIME:
                continue

            if current_time >= EXIT_TIME:
                continue

            # =============================================
            # ONLY AFTER PREVIOUS EXIT
            # =============================================

            if last_exit_time is not None:

                if candle_time <= last_exit_time:
                    continue

            # =============================================
            # VOLUME
            # =============================================

            vol = data["Volume"].iloc[i]

            avg_vol = data["Volume"].iloc[i-20:i].mean()

            if avg_vol == 0:
                continue

            # =============================================
            # SPIKE
            # =============================================

            spike = vol / avg_vol

            if spike < SPIKE_THRESHOLD:
                continue

            # =============================================
            # PRICE
            # =============================================

            close = data["Close"].iloc[i]

            open_price = data["Open"].iloc[i]

            rsi = data["RSI"].iloc[i]

            if pd.isna(rsi):
                continue

            # =============================================
            # EMA VALUES
            # =============================================

            e9 = data["EMA9"].iloc[i]
            e15 = data["EMA15"].iloc[i]
            e21 = data["EMA21"].iloc[i]
            e50 = data["EMA50"].iloc[i]
            e100 = data["EMA100"].iloc[i]
            e200 = data["EMA200"].iloc[i]

            # =============================================
            # BUY CONDITION
            # ONLY UPSIDE ENTRY
            # =============================================

            buy = (

                rsi > RSI_LEVEL and

                close > e9 > e15 > e21 > e50 > e100 > e200 and

                close > open_price
            )

            if not buy:
                continue

            # =============================================
            # ENTRY
            # =============================================

            entry_price = data["Open"].iloc[i+1]

            entry_time = data.index[i+1]

            # =============================================
            # QUANTITY
            # =============================================

            qty = int(CAPITAL / entry_price)

            if qty <= 0:
                continue

            invested = qty * entry_price

            # =============================================
            # DEFAULT EXIT
            # =============================================

            exit_price = entry_price

            exit_time = entry_time

            exit_reason = "HOLD"

            # =============================================
            # EXIT LOOP
            # =============================================

            for j in range(i+2, len(data)):

                current_price = data["Close"].iloc[j]

                current_loop_time = data.index[j].time()

                # =========================================
                # 3 PM FORCE EXIT
                # =========================================

                if current_loop_time >= EXIT_TIME:

                    exit_price = current_price

                    exit_time = data.index[j]

                    exit_reason = "3PM FORCE EXIT"

                    break

                # =========================================
                # STOPLOSS
                # =========================================

                if current_price <= entry_price * (1 - SL_PCT):

                    exit_price = current_price

                    exit_time = data.index[j]

                    exit_reason = "STOPLOSS"

                    break

                # =========================================
                # EMA EXIT
                # =========================================

                if current_price < data["EMA9"].iloc[j]:

                    exit_price = current_price

                    exit_time = data.index[j]

                    exit_reason = "EMA EXIT"

                    break

            # =============================================
            # PNL
            # =============================================

            pnl_per_share = exit_price - entry_price

            total_pnl = pnl_per_share * qty

            trade_return = (

                (total_pnl / invested) * 100

            )

            capital_after = CAPITAL + total_pnl

            # =============================================
            # SAVE TRADE
            # =============================================

            trades.append([

                stock,

                entry_time,
                exit_time,

                entry_price,
                exit_price,

                qty,

                invested,

                spike,

                total_pnl,

                trade_return,

                capital_after,

                exit_reason
            ])

            # =============================================
            # UPDATE CAPITAL
            # =============================================

            CAPITAL = capital_after

            last_exit_time = exit_time

    except Exception as e:

        print(f"ERROR in {stock} : {e}")

# =========================================================
# RESULTS
# =========================================================

win = 0
loss = 0

print("\n=========== ONLY BUY STRATEGY ==========\n")

for t in trades:

    if t[8] > 0:
        win += 1
    else:
        loss += 1

    print(

        f"{t[0]:12} | "

        f"BUY {t[1]} | "

        f"SELL {t[2]} | "

        f"Qty {t[5]} | "

        f"Spike {t[7]:.2f}x | "

        f"Entry {t[3]:.2f} | "

        f"Exit {t[4]:.2f} | "

        f"PnL ₹{t[8]:.2f} | "

        f"Return {t[9]:.2f}% | "

        f"Capital ₹{t[10]:.2f} | "

        f"{t[11]}"
    )

# =========================================================
# SUMMARY
# =========================================================

total = len(trades)

winrate = (

    (win / total) * 100

    if total else 0
)

total_profit = CAPITAL - START_CAPITAL

print("\n==============================")

print("START CAPITAL :", round(START_CAPITAL, 2))

print("FINAL CAPITAL :", round(CAPITAL, 2))

if total_profit >= 0:

    print("TOTAL PROFIT  : ₹", round(total_profit, 2))

else:

    print("TOTAL LOSS    : ₹", round(abs(total_profit), 2))

print("TOTAL TRADES  :", total)

print("WIN           :", win)

print("LOSS          :", loss)

print("WIN RATE      :", round(winrate, 2), "%")

print("==============================")

# हया कोड मध्ये काय काम होत लक्षात ठेवणे # 
# BUY ENTRY फक्त UP TREND मध्ये होईल.
#RSI 60 पेक्षा जास्त असेल तरच ENTRY मिळेल.
#Volume Spike 8X पेक्षा जास्त हवा.
#Price सर्व EMA च्या वर हवा:
#EMA9 > EMA15 > EMA21 > EMA50 > EMA100 > EMA200
#Candle GREEN असावी म्हणजे Close > Open.
#Entry पुढच्या 5 मिनिट candle च्या OPEN वर होईल.
#Entry Time फक्त 9:20 AM ते 3:00 PM मध्येच होईल.
#एका वेळेस फक्त 1 TRADE चालेल.
#DOWN SIDE / SHORT ENTRY नाही.
#STOPLOSS = Entry पासून 2% खाली.
#EXIT होईल जर Price EMA9 खाली गेला.
#3:00 PM ला सर्व TRADE FORCE EXIT होतील.
#Full Capital एका trade मध्ये वापरलं जाईल.
#EXIT नंतरच पुढचा TRADE सुरू होईल.
#Output मध्ये BUY Time, SELL Time, Entry, Exit, Profit/Loss सगळं दिसेल.