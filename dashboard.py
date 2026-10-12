import os
import json
import streamlit as st
import yfinance as yf

STATE_FILE = "portfolio_state.json"
MAX_CONCURRENT_POSITIONS = 5
PARTIAL_TP_ATR_MULTIPLIER = 2.5

st.set_page_config(layout="wide", page_title="BSJP Algo Trading Dashboard")

st.markdown("""
<style>
.stock-card {
    background-color: #ffffff;
    color: #000000;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    font-size: 0.9em;
}
.stock-card h3 {
    color: #000000;
    margin-top: 0;
    margin-bottom: 10px;
}
.stock-card p {
    margin: 4px 0;
    color: #333333;
}
.profit { color: #2ecc71 !important; font-weight: bold; font-size: 1.5em; margin: 0; }
.loss { color: #e74c3c !important; font-weight: bold; font-size: 1.5em; margin: 0; }
hr.card-divider { border-top: 1px solid #eeeeee; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"positions": []}
    try:
        with open(STATE_FILE, "r") as file:
            return json.load(file)
    except Exception:
        return {"positions": []}

state = load_state()
active_positions = state.get("positions", [])

st.title("📊 Swing Trading Dashboard")

col_meta1, col_meta2 = st.columns(2)
with col_meta1:
    st.metric("Total Posisi Aktif", f"{len(active_positions)} / {MAX_CONCURRENT_POSITIONS}")
with col_meta2:
    st.metric("Sisa Kuota Slot", f"{MAX_CONCURRENT_POSITIONS - len(active_positions)}")

st.write("---")

if not active_positions:
    st.info("Tidak ada posisi aktif dalam portofolio saat ini. Jalankan daily_scanner.py untuk mencari sinyal.")
else:
    live_data = {}
    for pos in active_positions:
        t = pos["ticker"]
        t_jk = t if t.endswith(".JK") else f"{t}.JK"
        try:
            ticker_obj = yf.Ticker(t_jk)
            todays_data = ticker_obj.history(period="1d")
            if not todays_data.empty:
                live_data[t] = float(todays_data["Close"].iloc[-1])
            else:
                live_data[t] = pos["entry_price"]
        except Exception:
            live_data[t] = pos["entry_price"]

    cols = st.columns(4) 
    for idx, pos in enumerate(active_positions):
        col_idx = idx % 4
        with cols[col_idx]:
            ticker = pos["ticker"]
            entry_price = pos["entry_price"]
            current_sl = pos["current_stop_loss"]
            atr_at_entry = pos["atr_at_entry"]
            partial_tp_price = entry_price + (PARTIAL_TP_ATR_MULTIPLIER * atr_at_entry)
            
            current_price = live_data.get(ticker, entry_price)
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
            
            color_class = "profit" if pnl_pct >= 0 else "loss"
            status_text = "HOLD (PROFIT)" if pnl_pct >= 0 else "HOLD (NYANGKUT)"
            
            if current_price <= current_sl:
                status_text = "🚨 WAJIB JUAL (KENA SL)"
            elif pos["partial_tp_hit"]:
                status_text = "💰 PARTIAL TP TERCAPAI"

            card_html = f"""
            <div class="stock-card">
                <h3>{ticker.split('.')[0]}</h3>
                <p class="{color_class}">{pnl_pct:.2f}%</p>
                <p><b>{status_text}</b></p>
                <hr class="card-divider">
                <p>Entry: <b>Rp {entry_price}</b></p>
                <p>Live: <b>Rp {current_price:.2f}</b></p>
                <p>SL: <b>Rp {current_sl:.2f}</b></p>
                <p>Target TP: <b>Rp {partial_tp_price:.2f}</b></p>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)