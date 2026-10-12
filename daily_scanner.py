import os
import json
from datetime import datetime

import yfinance as yf
import pandas as pd

import stock_data
from backtester import SECOND_LINER_UNIVERSE, MAX_CONCURRENT_POSITIONS, evaluate_entry_conditions
import telegram_notifier

STATE_FILE = "portfolio_state.json"
LOOKBACK_PERIOD = "2y"
PARTIAL_TP_ATR_MULTIPLIER = 2.5

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"positions": []}
    try:
        with open(STATE_FILE, "r") as file:
            return json.load(file)
    except Exception:
        return {"positions": []}

def save_state(state):
    with open(STATE_FILE, "w") as file:
        json.dump(state, file, indent=4)

def fetch_universe_data(ticker_codes, lookback_period=LOOKBACK_PERIOD):
    tickers = [code if code.endswith(".JK") else f"{code}.JK" for code in ticker_codes]
    print(f"Mengunduh data historis {lookback_period} untuk {len(tickers)} saham...")
    try:
        data = yf.download(
            tickers=tickers,
            period=lookback_period,
            interval="1d",
            group_by="ticker",
            threads=True,
            progress=False
        )
        if data is None or data.empty:
            print("Peringatan: data dari yfinance kosong.")
            return pd.DataFrame()
        print("Data historis berhasil diunduh.")
        return data
    except Exception as error:
        print(f"Gagal mengunduh data historis. Detail error: {error}")
        return pd.DataFrame()

def build_ticker_frames(batch_data, ticker_codes):
    ticker_frames = {}
    for ticker in ticker_codes:
        frame = stock_data.extract_ticker_frame(batch_data, ticker)
        if frame is not None and not frame.empty:
            ticker_frames[ticker] = frame
    return ticker_frames

def process_exit_phase(state, ticker_frames):
    alerts = []
    remaining_positions = []
    for position in state["positions"]:
        ticker = position["ticker"]
        frame = ticker_frames.get(ticker)
        if frame is None or frame.empty:
            remaining_positions.append(position)
            continue
        today_close = float(frame["Close"].iloc[-1])
        today_date = str(frame.index[-1].date())
        entry_price = position["entry_price"]
        atr_at_entry = position["atr_at_entry"]
        partial_tp_price = entry_price + (PARTIAL_TP_ATR_MULTIPLIER * atr_at_entry)
        if not position["partial_tp_hit"] and today_close >= partial_tp_price:
            position["partial_tp_hit"] = True
            position["partial_tp_price"] = round(partial_tp_price, 2)
            position["partial_tp_date"] = today_date
            alerts.append({
                "ticker": ticker,
                "type": "PARTIAL_TP",
                "price": round(partial_tp_price, 2)
            })
        if today_close <= position["current_stop_loss"]:
            exit_reason = "Trailing-Stop" if position["trailing_activated"] else "Initial-Stop-Loss"
            alerts.append({
                "ticker": ticker,
                "type": "FULL_EXIT",
                "price": round(position["current_stop_loss"], 2),
                "exit_reason": exit_reason
            })
            continue
        if today_close > position["highest_since_entry"]:
            position["highest_since_entry"] = today_close
        if today_close > entry_price:
            position["trailing_activated"] = True
        if position["trailing_activated"]:
            atr_current = stock_data.calculate_atr(frame)
            if atr_current is not None and atr_current > 0:
                trailing_candidate = stock_data.calculate_trailing_stop(position["highest_since_entry"], atr_current)
                if trailing_candidate > position["current_stop_loss"]:
                    position["current_stop_loss"] = trailing_candidate
        remaining_positions.append(position)
    state["positions"] = remaining_positions
    return alerts

def process_entry_phase(state, ticker_frames, ticker_codes):
    alerts = []
    active_tickers = set(position["ticker"] for position in state["positions"])
    available_slots = MAX_CONCURRENT_POSITIONS - len(state["positions"])
    if available_slots <= 0:
        return alerts
    candidates = []
    for ticker in ticker_codes:
        if ticker in active_tickers:
            continue
        frame = ticker_frames.get(ticker)
        if frame is None or frame.empty:
            continue
        entry_signal = evaluate_entry_conditions(frame)
        if entry_signal["is_valid"]:
            candidates.append((ticker, frame, entry_signal))
    # Ranking: skor tertinggi duluan, konsisten sama backtester.py -- biar hasil
    # live gak beda logic sama yang udah divalidasi lewat backtest.
    candidates.sort(key=lambda candidate: candidate[2]["score"], reverse=True)
    for ticker, frame, entry_signal in candidates[:available_slots]:
        entry_price = round(entry_signal["entry_price"], 2)
        atr_value = entry_signal["atr_value"]
        initial_stop_loss = entry_signal["initial_stop_loss"]
        partial_tp_price = round(entry_price + (PARTIAL_TP_ATR_MULTIPLIER * atr_value), 2)
        entry_date = str(frame.index[-1].date())
        new_position = {
            "ticker": ticker,
            "entry_date": entry_date,
            "entry_price": entry_price,
            "atr_at_entry": atr_value,
            "entry_score": entry_signal["score"],
            "current_stop_loss": initial_stop_loss,
            "highest_since_entry": entry_price,
            "trailing_activated": False,
            "partial_tp_hit": False,
            "partial_tp_price": None,
            "partial_tp_date": None
        }
        state["positions"].append(new_position)
        alerts.append({
            "ticker": ticker,
            "entry_price": entry_price,
            "initial_stop_loss": initial_stop_loss,
            "partial_tp_price": partial_tp_price,
            "entry_score": entry_signal["score"]
        })
    return alerts

def format_exit_alerts_message(exit_alerts):
    full_exit_alerts = [alert for alert in exit_alerts if alert["type"] == "FULL_EXIT"]
    partial_alerts = [alert for alert in exit_alerts if alert["type"] == "PARTIAL_TP"]
    lines = ["🚨 <b>ALERT SWING TRADING</b> 🚨", ""]
    if full_exit_alerts:
        lines.append("🔴 <b>INSTRUKSI JUAL HARI INI:</b>")
        lines.append("")
        for alert in full_exit_alerts:
            lines.append(f"• JUAL SEMUA {alert['ticker']} di {alert['price']} ({alert['exit_reason']})")
            lines.append("")
    if partial_alerts:
        lines.append("🟡 <b>PARTIAL TAKE PROFIT:</b>")
        lines.append("")
        for alert in partial_alerts:
            lines.append(f"• JUAL SETENGAH {alert['ticker']} di {alert['price']}")
            lines.append("")
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)

def format_entry_alerts_message(entry_alerts):
    lines = ["🚨 <b>ALERT SWING TRADING</b> 🚨", "", "🟢 <b>INSTRUKSI BELI HARI INI:</b>", ""]
    for alert in entry_alerts:
        lines.append(f"• BELI {alert['ticker']} di {alert['entry_price']} (Skor: {alert['entry_score']})")
        lines.append(f"  SL: {round(alert['initial_stop_loss'], 2)} | Partial TP: {alert['partial_tp_price']}")
        lines.append("")
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)

def print_dashboard(state, exit_alerts, entry_alerts):
    print("")
    print("========================================")
    print(f"DAILY SCANNER SWING TRADING - {datetime.now().date()}")
    print("========================================")
    print("")
    print("[A] STATUS POSISI AKTIF")
    print("----------------------------------------")
    if not state["positions"]:
        print("Tidak ada posisi aktif saat ini.")
    else:
        for position in state["positions"]:
            partial_tp_price = round(position["entry_price"] + (PARTIAL_TP_ATR_MULTIPLIER * position["atr_at_entry"]), 2)
            status_tp = "SUDAH TERCAPAI" if position["partial_tp_hit"] else "BELUM"
            print(f"{position['ticker']} | Entry {position['entry_date']} @ {position['entry_price']} | SL Saat Ini: {round(position['current_stop_loss'], 2)} | Partial TP: {partial_tp_price} ({status_tp})")
    print("")
    print("[B] INSTRUKSI JUAL HARI INI")
    print("----------------------------------------")
    full_exit_alerts = [alert for alert in exit_alerts if alert["type"] == "FULL_EXIT"]
    partial_alerts = [alert for alert in exit_alerts if alert["type"] == "PARTIAL_TP"]
    if not full_exit_alerts and not partial_alerts:
        print("Tidak ada instruksi jual hari ini.")
    else:
        for alert in full_exit_alerts:
            print(f"JUAL SEMUA {alert['ticker']} di sekitar {alert['price']} (Alasan: {alert['exit_reason']})")
        for alert in partial_alerts:
            print(f"JUAL SETENGAH {alert['ticker']} di sekitar {alert['price']} (Partial Take Profit tercapai)")
    print("")
    print("[C] INSTRUKSI BELI HARI INI")
    print("----------------------------------------")
    if not entry_alerts:
        print("Tidak ada sinyal beli baru hari ini.")
    else:
        for alert in entry_alerts:
            print(f"BELI {alert['ticker']} di {alert['entry_price']} | Skor: {alert['entry_score']} | SL: {round(alert['initial_stop_loss'], 2)} | Partial TP: {alert['partial_tp_price']}")
    print("========================================")

def main():
    print("MENJALANKAN DAILY SCANNER SWING TRADING")
    state = load_state()
    batch_data = fetch_universe_data(SECOND_LINER_UNIVERSE, LOOKBACK_PERIOD)
    if batch_data.empty:
        print("Proses dihentikan karena data pasar tidak tersedia.")
        return
    ticker_frames = build_ticker_frames(batch_data, SECOND_LINER_UNIVERSE)
    exit_alerts = process_exit_phase(state, ticker_frames)
    entry_alerts = []
    if len(state["positions"]) < MAX_CONCURRENT_POSITIONS:
        entry_alerts = process_entry_phase(state, ticker_frames, SECOND_LINER_UNIVERSE)
    save_state(state)
    if exit_alerts:
        telegram_notifier.send_telegram_message(format_exit_alerts_message(exit_alerts))
    if entry_alerts:
        telegram_notifier.send_telegram_message(format_entry_alerts_message(entry_alerts))
    print_dashboard(state, exit_alerts, entry_alerts)

if __name__ == "__main__":
    main()  
