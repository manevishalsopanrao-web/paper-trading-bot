import yfinance as yf
import pandas as pd
from flask import Flask
from datetime import datetime

# ==================================
# STOCK LIST
# ==================================

stocks = [
"KDDL.NS",
"YASHO.NS",
"CARYSIL.NS",
"NOVARTIND.NS",
"ENRIN.NS",
"ERIS.NS",
"DREDGECORP.NS",
"FOSECOIND.NS",
"AVALON.NS",
"TATACOMM.NS",
"NEOGEN.NS",
"BALAMINES.NS",
"GVT&D.NS",
"NIBE.NS",
"SMLMAH.NS",
"NGLFINE.NS",
"ASTRAMICRO.NS",
"DATAPATTNS.NS",
"ADVAIT.NS",
"QPOWER.NS",
"AZAD.NS",
"E2E.NS",
"SAFARI.NS",
"KICL.NS",
"SCHNEIDER.NS",
"INDOTECH.NS",
"SIEMENS.NS",
"ATLANTAELE.NS",
"SANSERA.NS",
"AUTOAXLES.NS",
"VENUSREM.NS",
"SHAILY.NS",
"MANKIND.NS",
"SEAMECLTD.NS",
"HINDALCO.NS",
"THANGAMAYL.NS",
"GRPLTD.NS",
"HALEOSLABS.NS",
"TIMKEN.NS",
"APOLSINHOT.NS",
"VELJAN.NS",
"CENTUM.NS",
"CHENNPETRO.NS",
"KMEW.NS",
"PAYTM.NS",
"TECHNVISN.NS",
"TEAMLEASE.NS",
"PRIVISCL.NS",
"WELCORP.NS",
"TAALTECH.NS",
"RELIANCE.NS",
"CUMMINSIND.NS",
"KPL.NS",
"CHEVIOT.NS",
"MALLCOM.NS",
"TIINDIA.NS",
"GRINDWELL.NS",
"MACPOWER.NS",
"SENORES.NS",
"NETWEB.NS",
"ZENTEC.NS",
"FRONTSP.NS",
"TVSMOTOR.NS",
"CRISIL.NS",
"HESTERBIO.NS",
"KIRLPNU.NS",
"RRKABEL.NS",
"NATCOPHARM.NS",
"TORNTPOWER.NS",
"ZYDUSLIFE.NS",
"VHL.NS",
"LUMAXIND.NS",
"SYRMA.NS",
"SEDEMAC.NS",
"NAM-INDIA.NS",
"BETA.NS",
"ARMANFIN.NS",
"SHILCTECH.NS",
"GRWRHITECH.NS",
"ETHOSLTD.NS",
"BHARATFORG.NS",
"BBL.NS",
"AAVAS.NS",
"NILE.NS",
"NPST.NS",
"MGL.NS",
"LUMAXTECH.NS",
"SWANDEF.NS",
"INOXINDIA.NS",
"SAILIFE.NS",
"KRISHNADEF.NS",
"POLICYBZR.NS",
"EMCURE.NS",
"SANOFICONR.NS",
"PHOENIXLTD.NS",
"BAJAJFINSV.NS",
"EIMCOELECO.NS",
"BALKRISIND.NS",
"CDSL.NS",
"ADANIENSOL.NS",
"GRASIM.NS",
"COCHINSHIP.NS",
"COCKERILL.NS",
"ICICIAMC.NS",
"LAURUSLABS.NS",
"HDFCAMC.NS",
"ENTERO.NS",
"IMFA.NS",
"HONDAPOWER.NS",
"MANORAMA.NS",
"CPPLUS.NS",
"AXISCADES.NS",
"DRAGARWQ.NS",
"DEEPAKNTR.NS",
"M&M.NS",
"NH.NS",
"INGERRAND.NS",
"AXISBANK.NS",
"360ONE.NS",
"INDIGO.NS",
"LGEINDIA.NS",
"MCX.NS",
"INDIAMART.NS",
"PRESTIGE.NS",
"TRANSPEK.NS",
"RPGLIFE.NS",
"KEI.NS",
"TRENT.NS",
"ANURAS.NS",
"TECHNOE.NS",
"LTTS.NS",
"ONESOURCE.NS",
"NSIL.NS",
"UNIVCABLES.NS",
"SCHAEFFLER.NS",
"GALAXYSURF.NS",
"VEEDOL.NS",
"PILANIINVS.NS",
"BSE.NS",
"MAXHEALTH.NS",
"MAZDOCK.NS",
"SUPREMEIND.NS",
"HAPPYFORGE.NS",
"CCL.NS",
"ABREL.NS",
"NUVAMA.NS",
"KRN.NS",
"FINEORG.NS",
"ALKYLAMINE.NS",
"ADANIPORTS.NS",
"CARTRADE.NS",
"PUNJABCHEM.NS",
"CHOLAFIN.NS",
"MFSL.NS",
"TCPLPACK.NS",
"WELINV.NS",
"JUBLCPL.NS",
"UNOMINDA.NS",
"HYUNDAI.NS",
"PIXTRANS.NS",
"MPSLTD.NS",
"JINDALPHOT.NS",
"SKFINDIA.NS",
"PERSISTENT.NS",
"MPHASIS.NS",
"PGHL.NS",
"JUBLPHARMA.NS",
"AUROPHARMA.NS",
"POLYMED.NS",
"OBEROIRLTY.NS",
"RACLGEAR.NS",
"ENDURANCE.NS",
"RATNAMANI.NS",
"HOMEFIRST.NS",
"NITTAGELA.NS",
"GODREJPROP.NS",
"ISGEC.NS",
"WAAREEENER.NS",
"KENNAMET.NS",
"WABAG.NS",
"MUTHOOTFIN.NS",
"KIRLOSENG.NS",
"ESCORTS.NS",
"CEATLTD.NS",
"BEML.NS",
"KINGFA.NS",
"TITAN.NS",
"OLECTRA.NS",
"TBOTEK.NS",
"GODREJCP.NS",
"ADOR.NS",
"KAMAHOLD.NS",
"WHEELS.NS",
"EPIGRAL.NS",
"FLUOROCHEM.NS",
"ICRA.NS",
"HAVELLS.NS",
"UBL.NS",
"TIIL.NS",
"TCS.NS",
"AVANTIFEED.NS",
"TRAVELFOOD.NS",
"VINATIORGA.NS",
"PIDILITIND.NS",
"MEDANTA.NS",
"THERMAX.NS",
"JSWDULUX.NS",
"DCMSHRIRAM.NS",
"JPOLYINVST.NS",
"KERNEX.NS",
"KOVAI.NS",
"KAJARIACER.NS",
"ASIANPAINT.NS",
"ALIVUS.NS",
"LUPIN.NS",
"SUNPHARMA.NS",
"COLPAL.NS",
"HAL.NS",
"JSWSTEEL.NS",
"ANUP.NS",
"TATACONSUM.NS",
"ACUTAAS.NS",
"NBIFIN.NS",
"ZOTA.NS",
"BLUESTARCO.NS",
"LT.NS",
"TATAELXSI.NS",
"JINDALSTEL.NS",
"INFY.NS",
"ICICIBANK.NS",
"COROMANDEL.NS",
"PNBHOUSING.NS",
"ASTRAL.NS",
"JBCHEPHARM.NS",
"GRAVITA.NS",
"APLAPOLLO.NS",
"DALBHARAT.NS",
"BIRLANU.NS",
"GRSE.NS",
"CERA.NS",
"BHARTIARTL.NS",
"DODLA.NS",
"TVSSRICHAK.NS",
"DEEPAKFERT.NS",
"WOCKPHARMA.NS",
"VOLTAS.NS",
"3BBLACKBIO.NS",
"ORISSAMINE.NS",
"PIRAMALFIN.NS",
"SUMMITSEC.NS",
"ACC.NS",
"GABRIEL.NS",
"IPCALAB.NS",
"LLOYDSME.NS",
"SWARAJENG.NS",
"VENKEYS.NS",
"BDL.NS",
"ALKEM.NS",
"RAINBOW.NS",
"AMBIKCO.NS",
"KPIL.NS",
"AKCAPIT.NS",
"SPECTRUM.NS",
"COFORGE.NS",
"TORNTPHARM.NS",
"LGBBROSLTD.NS",
"GOODLUCK.NS",
"BBTC.NS",
"VINDHYATEL.NS",
"CIPLA.NS",
"ADANIENT.NS",
"GKWLIMITED.NS",
"NESTLEIND.NS",
"HEROMOTOCO.NS",
"PGIL.NS",
"POWERMECH.NS",
"SJS.NS",
"JLHL.NS",
"THACKER.NS",
"HCLTECH.NS",
"KIRLOSBROS.NS",
"GANECOS.NS",
"NESCO.NS",
"FIEMIND.NS",
"METROBRAND.NS",
"GODREJIND.NS",
"VADILALIND.NS",
"BAYERCROP.NS",
"SRF.NS",
"SBILIFE.NS",
"AFFLE.NS",
"ANANDRATHI.NS",
"RANEHOLDIN.NS",
"RADICO.NS",
"AETHER.NS",
"NDGL.NS",
"TEGA.NS",
"BHARTIHEXA.NS",
"DRREDDY.NS",
"MIDWESTLTD.NS",
"AIAENG.NS",
"IKS.NS",
"STAR.NS",
"SHRIPISTON.NS",
"HINDUNILVR.NS",
"ADANIGREEN.NS",
"CAPLIPOINT.NS",
"GLENMARK.NS",
"STYLAMIND.NS",
"NILKAMAL.NS",
"VENUSPIPES.NS",
"SOBHA.NS",
"BANARISUG.NS",
"CREDITACC.NS",
"ACCELYA.NS",
"SANOFI.NS",
"PRUDENT.NS",
"GLAND.NS",
"BHARATRAS.NS",
"BRITANNIA.NS",
"SKFINDUS.NS",
"BLUEDART.NS",
"IMPAL.NS",
"GODFRYPHLP.NS",
"ABSLAMC.NS",
"CLEANMAX.NS",
"UNITDSPR.NS",
"FINCABLES.NS",
"CARBORUNIV.NS",
"JKCEMENT.NS",
"LUXIND.NS",
"SUNDARMFIN.NS",
"GLAXO.NS",
"AJANTPHARM.NS",
"INTERARCH.NS",
"VSTTILLERS.NS",
"TECHM.NS",
"TDPOWERSYS.NS",
"PFIZER.NS",
"CARERATING.NS",
"LALPATHLAB.NS",
"ICICIGI.NS",
"DMART.NS",
"VIJAYA.NS",
"BOSCH-HCIL.NS",
"ECLERX.NS",
"THEJO.NS",
"CONCORDBIO.NS",
"CHOLAHLDNG.NS",
"MASTEK.NS",
"DHANUKA.NS",
"LTM.NS",
"XPROINDIA.NS",
"STYRENIX.NS",
"SOLEX.NS",
"CORONA.NS",
"BUILDPRO.NS",
"DOMS.NS",
"KAYNES.NS",
"GESHIP.NS",
"TATVA.NS",
"DSSL.NS",
"NATIONSTD.NS",
"SUNCLAY.NS",
"POCL.NS",
"BASF.NS",
"IFBIND.NS",
"SASKEN.NS",
"PIIND.NS",
"KIRLOSIND.NS"
]

INTERVAL = "5m"
PERIOD = "1d"

results = []

# ==================================
# SCAN STOCKS
# ==================================

for stock in stocks:

    try:

        df = yf.download(
            stock,
            interval=INTERVAL,
            period=PERIOD,
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            continue

        # MultiIndex Fix
        if isinstance(df.columns, pd.MultiIndex):

            open_series = df[("Open", stock)]
            high_series = df[("High", stock)]
            low_series = df[("Low", stock)]
            close_series = df[("Close", stock)]

        else:

            open_series = df["Open"]
            high_series = df["High"]
            low_series = df["Low"]
            close_series = df["Close"]

        if len(close_series) < 2:
            continue

        close = float(close_series.iloc[-1])

        day_high = float(high_series.max())
        day_low = float(low_series.min())

        reward = close - day_low
        risk = day_high - close

        if risk <= 0:
            risk = 0.01

        r_factor = reward / risk

        green = int((close_series > open_series).sum())
        red = int((close_series < open_series).sum())

        strength = green - red

        results.append({
            "Stock": stock,
            "R Factor": round(r_factor, 2),
            "Green Candle": green,
            "Red Candle": red,
            "Strength": strength
        })

    except Exception as e:
        print(stock, ":", e)

# ==================================
# RESULT
# ==================================

result_df = pd.DataFrame(results)

if not result_df.empty:

    top5_down = result_df.sort_values(
        by=["Strength", "R Factor"],
        ascending=[True, True]
    ).head(5)

    print("\n")
    print("=" * 80)
    print("TOP 5 DOWN STOCKS")
    print("=" * 80)

    print(
        top5_down[
            [
                "Stock",
                "R Factor",
                "Green Candle",
                "Red Candle",
                "Strength"
            ]
        ].to_string(index=False)
    )
    top5_down.to_csv("signals.csv", index=False)

print("\nSignals Saved : signals.csv")


# ==================================
# FLASK DASHBOARD
# ==================================

app = Flask(__name__)

@app.route("/")
def home():

    if result_df.empty:
        return "<h1>No Data Found</h1>"

    return f"""
    <html>
    <head>

    <title>Top 5 Down Stocks</title>

    <meta http-equiv="refresh" content="5">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>

    body {{
        background:#0f172a;
        color:white;
        font-family:Arial;
        margin:10px;
    }}

    h1 {{
        text-align:center;
        color:#ef4444;
    }}

    h3 {{
        text-align:center;
        color:#cbd5e1;
    }}

    .box {{
        width:95%;
        margin:auto;
        background:#1e293b;
        padding:15px;
        border-radius:12px;
    }}

    table {{
        width:100%;
        border-collapse:collapse;
        background:#0f172a;
    }}

    th {{
        background:#dc2626;
        color:white;
        padding:10px;
    }}

    td {{
        padding:8px;
        text-align:center;
        border-bottom:1px solid #334155;
    }}

    .down {{
        color:#ef4444;
    }}

    </style>

    </head>

    <body>

    <h1>🔻 TOP 5 DOWN STOCKS</h1>

    <h3>Total Stocks : {len(result_df)}</h3>
    <h3>Last Update : {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}</h3>

    <div class="box">

        <h2 class="down">TOP 5 DOWN STOCKS</h2>

        {top5_down.to_html(index=False)}

    </div>

    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
