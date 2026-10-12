import json
import time as time_module
from datetime import datetime
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor, as_completed

import market_screener
import nlp_sentiment
import stock_data
import telegram_notifier

JAKARTA_TZ = ZoneInfo("Asia/Jakarta")
RESULTS_FILE = "signal_results.json"
CHECK_INTERVAL_SECONDS = 60
NEWS_WORKER_THREADS = 5

state = {
    "trading_date": None,
    "target_list": [],
    "daily_data": None,
    "screening_done": False,
    "notified_codes": set()
}

def reset_state_if_new_day():
    today = datetime.now(JAKARTA_TZ).date()
    if state["trading_date"] != today:
        state["trading_date"] = today
        state["target_list"] = []
        state["daily_data"] = None
        state["screening_done"] = False
        state["notified_codes"] = set()

def run_screening():
    target_list = market_screener.get_top_active_and_gainers()
    state["target_list"] = target_list
    if target_list:
        state["daily_data"] = stock_data.fetch_batch_daily_data(target_list)
    state["screening_done"] = True

def fetch_sentiment_for_codes(codes):
    sentiment_map = {}
    with ThreadPoolExecutor(max_workers=NEWS_WORKER_THREADS) as executor:
        future_to_code = {
            executor.submit(nlp_sentiment.analyze_stock_sentiment, code, market_screener.get_company_name(code)): code
            for code in codes
        }
        for future in as_completed(future_to_code):
            code = future_to_code[future]
            try:
                sentiment_map[code] = future.result()
            except Exception:
                sentiment_map[code] = {
                    "is_heavy_positive": False,
                    "score": 0,
                    "catalyst_summary": "Gagal mengambil berita"
                }
    return sentiment_map

def scan_target_list():
    codes = state["target_list"]
    if not codes:
        return []
    sentiment_map = fetch_sentiment_for_codes(codes)
    intraday_batch = stock_data.fetch_batch_5m_data(codes)
    signals = []
    for code in codes:
        if code in state["notified_codes"]:
            continue
        sentiment_result = sentiment_map.get(code)
        if not sentiment_result or not sentiment_result["is_heavy_positive"]:
            continue
        intraday_frame = stock_data.extract_ticker_frame(intraday_batch, code)
        volume_result = stock_data.detect_volume_anomaly(intraday_frame)
        if not volume_result["is_anomaly"]:
            continue
        daily_frame = stock_data.extract_ticker_frame(state["daily_data"], code)
        if daily_frame is None or daily_frame.empty:
            continue
        entry_price = float(intraday_frame.iloc[-1]["Close"])
        if not stock_data.is_uptrend(daily_frame, entry_price):
            continue
        risk_data = stock_data.calculate_dynamic_risk_management(daily_frame, entry_price)
        company_name = market_screener.get_company_name(code)
        signal = {
            "Nama Saham": company_name,
            "Katalis Berita": sentiment_result["catalyst_summary"],
            "% Lonjakan Volume": volume_result["spike_percentage"],
            "Harga Entry": risk_data["entry_price"],
            "Target": risk_data["take_profit"],
            "Stop-Loss": risk_data["stop_loss"]
        }
        signals.append(signal)
        state["notified_codes"].add(code)
        message = telegram_notifier.format_signal_message(
            company_name,
            sentiment_result["catalyst_summary"],
            volume_result["spike_percentage"],
            risk_data["entry_price"],
            risk_data["stop_loss"],
            risk_data["take_profit"],
            risk_data["risk_reward_ratio"],
            risk_data["sl_basis"]
        )
        telegram_notifier.send_telegram_message(message)
    return signals

def load_existing_results():
    try:
        with open(RESULTS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_results(new_signals):
    existing = load_existing_results()
    existing.extend(new_signals)
    with open(RESULTS_FILE, "w") as file:
        json.dump(existing, file, indent=4)

def run_forever():
    while True:
        reset_state_if_new_day()
        if stock_data.is_screening_time() and not state["screening_done"]:
            run_screening()
        if stock_data.is_pre_closing_session() and state["screening_done"]:
            new_signals = scan_target_list()
            if new_signals:
                save_results(new_signals)
        time_module.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    run_forever()