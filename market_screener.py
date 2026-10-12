import yfinance as yf
import pandas as pd

LIQUID_UNIVERSE = [
    "ACES.JK", "ADRO.JK", "AKRA.JK", "AMMN.JK", "AMRT.JK", "ANTM.JK", "ARTO.JK", "ASII.JK",
    "AUTO.JK", "AVIA.JK", "BBCA.JK", "BBNI.JK", "BBRI.JK", "BBTN.JK", "BMRI.JK", "BRIS.JK",
    "BRPT.JK", "BUKA.JK", "CPIN.JK", "CTRA.JK", "ESSA.JK", "EXCL.JK", "GOTO.JK", "ICBP.JK",
    "INCO.JK", "INDF.JK", "INDY.JK", "INKP.JK", "ISAT.JK", "ITMG.JK", "JPFA.JK", "JSMR.JK",
    "KLBF.JK", "MAPI.JK", "MBMA.JK", "MDKA.JK", "MEDC.JK", "PGAS.JK", "PGEO.JK", "PTBA.JK",
    "SIDO.JK", "SMGR.JK", "SMRA.JK", "TLKM.JK", "TOWR.JK", "UNTR.JK", "UNVR.JK"
]

COMPANY_NAMES = {
    "ACES": "Ace Hardware Indonesia", "ADRO": "Adaro Energy Indonesia", "AKRA": "AKR Corporindo",
    "AMMN": "Amman Mineral Internasional", "AMRT": "Sumber Alfaria Trijaya", "ANTM": "Aneka Tambang",
    "ARTO": "Bank Jago", "ASII": "Astra International", "AUTO": "Astra Otoparts",
    "AVIA": "Avia Avian", "BBCA": "Bank Central Asia", "BBNI": "Bank Negara Indonesia",
    "BBRI": "Bank Rakyat Indonesia", "BBTN": "Bank Tabungan Negara", "BMRI": "Bank Mandiri",
    "BRIS": "Bank Syariah Indonesia", "BRPT": "Barito Pacific", "BUKA": "Bukalapak.com",
    "CPIN": "Charoen Pokphand Indonesia", "CTRA": "Ciputra Development", "ESSA": "ESSA Industries Indonesia",
    "EXCL": "XL Axiata", "GOTO": "GoTo Gojek Tokopedia", "ICBP": "Indofood CBP Sukses Makmur",
    "INCO": "Vale Indonesia", "INDF": "Indofood Sukses Makmur", "INDY": "Indika Energy",
    "INKP": "Indah Kiat Pulp Paper", "ISAT": "Indosat Ooredoo Hutchison", "ITMG": "Indo Tambangraya Megah",
    "JPFA": "Japfa Comfeed Indonesia", "JSMR": "Jasa Marga", "KLBF": "Kalbe Farma",
    "MAPI": "Mitra Adiperkasa", "MBMA": "Merdeka Battery Materials", "MDKA": "Merdeka Copper Gold",
    "MEDC": "Medco Energi Internasional", "PGAS": "Perusahaan Gas Negara", "PGEO": "Pertamina Geothermal Energy",
    "PTBA": "Bukit Asam", "SIDO": "Industri Jamu Sido Muncul", "SMGR": "Semen Indonesia",
    "SMRA": "Summarecon Agung", "TLKM": "Telkom Indonesia", "TOWR": "Sarana Menara Nusantara",
    "UNTR": "United Tractors", "UNVR": "Unilever Indonesia"
}

TOP_N = 30

def get_company_name(ticker_code):
    return COMPANY_NAMES.get(ticker_code, ticker_code)

def fetch_market_snapshot():
    try:
        data = yf.download(
            tickers=LIQUID_UNIVERSE,
            period="2d",
            interval="1d",
            group_by="ticker",
            threads=True,
            progress=False
        )
        return data
    except Exception:
        return pd.DataFrame()

def build_screener_table(batch_data):
    records = []
    for ticker in LIQUID_UNIVERSE:
        try:
            frame = batch_data[ticker].dropna()
            if len(frame) < 2:
                continue
            previous_close = frame["Close"].iloc[-2]
            last_close = frame["Close"].iloc[-1]
            last_volume = frame["Volume"].iloc[-1]
            if previous_close == 0:
                continue
            change_percentage = ((last_close - previous_close) / previous_close) * 100
            records.append({
                "kode": ticker.replace(".JK", ""),
                "harga_terakhir": last_close,
                "perubahan_persen": round(change_percentage, 2),
                "volume": last_volume
            })
        except Exception:
            continue
    return pd.DataFrame(records)

def get_top_active_and_gainers():
    batch_data = fetch_market_snapshot()
    if batch_data.empty:
        return []
    table = build_screener_table(batch_data)
    if table.empty:
        return []
    top_gainers = table.sort_values(by="perubahan_persen", ascending=False).head(TOP_N)
    top_active = table.sort_values(by="volume", ascending=False).head(TOP_N)
    combined = pd.concat([top_gainers, top_active]).drop_duplicates(subset="kode")
    combined = combined.sort_values(by="volume", ascending=False).head(TOP_N)
    return combined["kode"].tolist()