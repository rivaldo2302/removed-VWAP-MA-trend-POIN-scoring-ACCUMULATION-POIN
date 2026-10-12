import warnings
import logging
import yfinance as yf
import pandas as pd

warnings.filterwarnings("ignore")
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

BLACKLIST = ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK', 'TLKM.JK', 'ASII.JK', 'BYAN.JK', 'AMMN.JK', 'BREN.JK', 'GOTO.JK', 'UNVR.JK', 'ICBP.JK', 'CPIN.JK', 'KLBF.JK', 'AMRT.JK']

ADTV_THRESHOLD = 2000000000
INPUT_FILE = "all_tickers.txt"
OUTPUT_FILE = "clean_universe.txt"

def load_tickers(file_path):
    tickers = []
    try:
        with open(file_path, "r") as file:
            for line in file:
                ticker = line.strip()
                if ticker:
                    tickers.append(ticker)
    except FileNotFoundError:
        print(f"File {file_path} tidak ditemukan")
        return []
    return tickers

def filter_blacklist(tickers):
    return [ticker for ticker in tickers if ticker not in BLACKLIST]

def fetch_price_data(tickers):
    if not tickers:
        return pd.DataFrame()
    try:
        data = yf.download(
            tickers=tickers,
            period="1mo",
            threads=True,
            group_by="ticker",
            progress=False
        )
        return data
    except Exception:
        return pd.DataFrame()

def extract_ticker_frame(batch_data, ticker):
    if batch_data is None or batch_data.empty:
        return None
    try:
        if isinstance(batch_data.columns, pd.MultiIndex):
            if ticker not in batch_data.columns.get_level_values(0):
                return None
            frame = batch_data[ticker].dropna()
        else:
            frame = batch_data.dropna()
        return frame
    except Exception:
        return None

def calculate_adtv(frame):
    if frame is None or frame.empty:
        return None
    try:
        transaction_value = (frame["Close"] * frame["Volume"]).dropna()
        if transaction_value.empty:
            return None
        return float(transaction_value.mean())
    except Exception:
        return None

def screen_tickers(tickers):
    qualified = []
    batch_data = fetch_price_data(tickers)
    for ticker in tickers:
        frame = extract_ticker_frame(batch_data, ticker)
        adtv = calculate_adtv(frame)
        if adtv is not None and adtv >= ADTV_THRESHOLD:
            qualified.append(ticker)
    return qualified

def save_results(tickers, file_path):
    with open(file_path, "w") as file:
        file.write(str(tickers))

def main():
    raw_tickers = load_tickers(INPUT_FILE)
    filtered_tickers = filter_blacklist(raw_tickers)
    qualified_tickers = screen_tickers(filtered_tickers)
    save_results(qualified_tickers, OUTPUT_FILE)
    print(f"Total ticker dibaca: {len(raw_tickers)}")
    print(f"Setelah blacklist: {len(filtered_tickers)}")
    print(f"Lolos ADTV >= {ADTV_THRESHOLD}: {len(qualified_tickers)}")
    print(f"Hasil disimpan ke {OUTPUT_FILE}")

if __name__ == "__main__":
    main()