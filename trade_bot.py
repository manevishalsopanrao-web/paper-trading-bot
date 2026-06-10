import requests
import yfinance as yf
import pandas as pd
import pytz
import time

# ==========================
# TELEGRAM CONFIG
# ==========================
BOT_TOKEN = "8963361139:AAFcppLM_XRprJQ02PuSAglNIba7jy2Pk5g"
CHAT_ID = "6456813373"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": message
        })
    except Exception as e:
        print("Telegram Error:", e)

# ==========================
# STOCK LIST
# ==========================
stocks = [
    "MARUTI.NS","M&M.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS",
    "EICHERMOT.NS","TVSMOTOR.NS","ASHOKLEY.NS","BHARATFORG.NS",
    "HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","AXISBANK.NS",
    "KOTAKBANK.NS","PNB.NS","BANKBARODA.NS","TCS.NS",
    "INFY.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS",
    "PERSISTENT.NS","COFORGE.NS","SUNPHARMA.NS","DIVISLAB.NS",
    "DRREDDY.NS","CIPLA.NS","SAIL.NS","NMDC.NS",
    "LUPIN.NS","AUROPHARMA.NS","RELIANCE.NS","NTPC.NS",
    "POWERGRID.NS","IOC.NS","BPCL.NS","ONGC.NS"
]

india = pytz.timezone("Asia/Kolkata")
DMI_LENGTH = 2

# ==========================
# DMI FUNCTION
# ==========================
def calculate_dmi(df, period=2):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    plus_dm = high.diff()
    minus_dm = -low.diff()

    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).sum()

    plus_di = 100 * plus_dm.rolling(period).sum() / atr
    minus_di = 100 * minus_dm.rolling(period).sum() / atr

    return plus_di, minus_di

# ==========================
# ALERT TRACKING (duplicate avoid)
# ==========================
sent_alerts = set()

print("Scanning started...")

# ==========================
# MAIN LOOP
# ==========================
while True:

    results = []

    for stock in stocks:

        try:
            df = yf.download(
                stock,
                period="1d",
                interval="5m",
                auto_adjust=True,
                progress=False
            )

            if df.empty:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            try:
                df.index = df.index.tz_convert(india)
            except:
                df.index = df.index.tz_localize("UTC").tz_convert(india)

            # EMA
            for span in [9,15,21,50,100,200]:
                df[f"EMA{span}"] = df["Close"].ewm(span=span).mean()

            # MACD
            ema12 = df["Close"].ewm(span=12).mean()
            ema26 = df["Close"].ewm(span=26).mean()
            df["MACD"] = ema12 - ema26
            df["SIGNAL"] = df["MACD"].ewm(span=9).mean()

            # DMI
            plus_di, minus_di = calculate_dmi(df, DMI_LENGTH)
            df["PLUS_DI"] = plus_di
            df["MINUS_DI"] = minus_di

            # CHECK LAST CANDLE ONLY (fast + live)
            row = df.iloc[-1]
            idx = df.index[-1]

            if idx.hour == 9 and 15 <= idx.minute <= 45:

                close = row["Close"]

                ema_negative = (
                    close < row["EMA9"] and
                    close < row["EMA15"] and
                    close < row["EMA21"] and
                    close < row["EMA50"] and
                    close < row["EMA100"] and
                    close < row["EMA200"]
                )

                macd_negative = row["MACD"] < row["SIGNAL"]
                dmi_negative = row["MINUS_DI"] >= 60

                if ema_negative and macd_negative and dmi_negative:

                    alert_key = f"{stock}-{idx}"

                    if alert_key not in sent_alerts:
                        sent_alerts.add(alert_key)

                        msg = (
                            f"📉 Negative Trend Alert\n\n"
                            f"Stock: {stock}\n"
                            f"Time: {idx.strftime('%H:%M')}\n"
                            f"DMI: {row['MINUS_DI']:.2f}\n"
                            f"MACD: Bearish\n"
                        )

                        print(msg)
                        send_telegram(msg)

        except Exception as e:
            print(f"{stock} Error: {e}")

    print("Scan complete. Sleeping 60 sec...\n")
    time.sleep(60)
