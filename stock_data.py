import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, time
from zoneinfo import ZoneInfo

JAKARTA_TZ = ZoneInfo("Asia/Jakarta")
PRE_CLOSING_START = time(15, 30)
PRE_CLOSING_END = time(15, 50)
SCREENING_HOUR = 15
SCREENING_MINUTE = 0

LIQUIDITY_LOOKBACK_DAYS = 20
LIQUIDITY_ADTV_THRESHOLD = 10000000000
ATR_PERIOD = 14
MA_TREND_PERIOD = 50
MA_LONG_PERIOD = 200
PULLBACK_TOLERANCE_PERCENTAGE = 2.0
INITIAL_SL_ATR_MULTIPLIER = 1.0
TRAILING_ATR_MULTIPLIER = 3.0

MFI_PERIOD = 14
CMF_PERIOD = 20
OBV_MA_PERIOD = 20
VWAP_PERIOD = 20
MFI_HEALTHY_MIN = 40
MFI_HEALTHY_MAX = 80
WEEKLY_MA_PERIOD = 50
SQUEEZE_SHORT_PERIOD = 5
SQUEEZE_BASELINE_PERIOD = 20
SQUEEZE_RATIO_THRESHOLD = 0.75

def is_pre_closing_session(current_time=None):
    now = current_time or datetime.now(JAKARTA_TZ)
    now_time = now.timetz().replace(tzinfo=None)
    return PRE_CLOSING_START <= now_time <= PRE_CLOSING_END

def is_screening_time(current_time=None):
    now = current_time or datetime.now(JAKARTA_TZ)
    return now.hour == SCREENING_HOUR and now.minute == SCREENING_MINUTE

def fetch_batch_5m_data(ticker_codes):
    tickers = [code if code.endswith(".JK") else f"{code}.JK" for code in ticker_codes]
    try:
        data = yf.download(
            tickers=tickers,
            period="1d",
            interval="5m",
            group_by="ticker",
            threads=True,
            progress=False
        )
        return data
    except Exception:
        return pd.DataFrame()

def fetch_batch_daily_data(ticker_codes, lookback_period="3y"):
    tickers = [code if code.endswith(".JK") else f"{code}.JK" for code in ticker_codes]
    try:
        data = yf.download(
            tickers=tickers,
            period=lookback_period,
            interval="1d",
            group_by="ticker",
            threads=True,
            progress=False
        )
        return data
    except Exception:
        return pd.DataFrame()

def extract_ticker_frame(batch_data, ticker_code):
    if batch_data is None or batch_data.empty:
        return None
    ticker = ticker_code if ticker_code.endswith(".JK") else f"{ticker_code}.JK"
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

def calculate_adtv(daily_frame, period=LIQUIDITY_LOOKBACK_DAYS):
    # Average Daily Transaction Value (Rupiah) dalam N hari terakhir.
    # Dipakai buat mencatat likuiditas tiap trade (bukan buat menggagalkan entry),
    # supaya bisa dianalisis nanti: trade di saham sepi hasilnya beda gak dibanding yang ramai.
    if daily_frame is None or len(daily_frame) < period:
        return None
    daily_value = daily_frame["Close"] * daily_frame["Volume"]
    adtv_series = daily_value.rolling(window=period).mean()
    latest_adtv = adtv_series.iloc[-1]
    if pd.isna(latest_adtv):
        return None
    return float(latest_adtv)

def is_liquid_enough(daily_frame, period=LIQUIDITY_LOOKBACK_DAYS, threshold=LIQUIDITY_ADTV_THRESHOLD):
    latest_adtv = calculate_adtv(daily_frame, period)
    if latest_adtv is None:
        return False
    return latest_adtv > threshold

def calculate_moving_average(daily_frame, period=MA_TREND_PERIOD):
    if daily_frame is None or len(daily_frame) < period:
        return None
    ma_series = daily_frame["Close"].rolling(window=period).mean()
    last_ma = ma_series.iloc[-1]
    if pd.isna(last_ma):
        return None
    return float(last_ma)

def calculate_close_to_ma50_distance_percentage(daily_frame, period=MA_TREND_PERIOD):
    ma_value = calculate_moving_average(daily_frame, period)
    if ma_value is None or ma_value == 0:
        return None
    day_close = float(daily_frame["Close"].iloc[-1])
    distance_percentage = ((day_close - ma_value) / ma_value) * 100
    return distance_percentage

def is_close_near_ma50(daily_frame, period=MA_TREND_PERIOD, tolerance_percentage=PULLBACK_TOLERANCE_PERCENTAGE):
    distance_percentage = calculate_close_to_ma50_distance_percentage(daily_frame, period)
    if distance_percentage is None:
        return False
    return abs(distance_percentage) <= tolerance_percentage

def is_higher_low_bounce(daily_frame):
    if daily_frame is None or len(daily_frame) < 2:
        return False
    today_close = float(daily_frame["Close"].iloc[-1])
    yesterday_low = float(daily_frame["Low"].iloc[-2])
    today_volume = float(daily_frame["Volume"].iloc[-1])
    yesterday_volume = float(daily_frame["Volume"].iloc[-2])
    
    higher_low_confirmed = today_close > yesterday_low
    volume_confirmed = today_volume > yesterday_volume
    return higher_low_confirmed and volume_confirmed

def is_ma50_trending_up(daily_frame, period=MA_TREND_PERIOD, lookback=5):
    if daily_frame is None or len(daily_frame) < period + lookback:
        return False
    current_ma50 = calculate_moving_average(daily_frame, period)
    past_frame = daily_frame.iloc[:-lookback]
    past_ma50 = calculate_moving_average(past_frame, period)
    if current_ma50 is None or past_ma50 is None:
        return False
    return current_ma50 > past_ma50

def calculate_recent_range_average(daily_frame, period=SQUEEZE_SHORT_PERIOD):
    if daily_frame is None or len(daily_frame) < period:
        return None
    recent = daily_frame.tail(period)
    range_series = recent["High"] - recent["Low"]
    return float(range_series.mean())

def calculate_baseline_range_average(daily_frame, period=SQUEEZE_BASELINE_PERIOD):
    if daily_frame is None or len(daily_frame) < period:
        return None
    recent = daily_frame.tail(period)
    range_series = recent["High"] - recent["Low"]
    return float(range_series.mean())

def is_volatility_squeeze(daily_frame, short_period=SQUEEZE_SHORT_PERIOD, baseline_period=SQUEEZE_BASELINE_PERIOD, ratio_threshold=SQUEEZE_RATIO_THRESHOLD):
    recent_range_average = calculate_recent_range_average(daily_frame, short_period)
    baseline_range_average = calculate_baseline_range_average(daily_frame, baseline_period)
    if recent_range_average is None or baseline_range_average is None or baseline_range_average == 0:
        return False
    return recent_range_average <= (baseline_range_average * ratio_threshold)

def evaluate_quiet_accumulation_signal(daily_frame):
    obv_above_average = is_obv_above_average(daily_frame)
    vwap_value = calculate_vwap(daily_frame)
    close_price = float(daily_frame["Close"].iloc[-1])
    above_vwap = vwap_value is not None and close_price > vwap_value
    is_valid = obv_above_average and above_vwap
    return {
        "is_valid": is_valid,
        "obv_above_average": obv_above_average,
        "vwap_value": round(vwap_value, 2) if vwap_value is not None else None,
        "above_vwap": above_vwap
    }

def calculate_atr(daily_frame, period=ATR_PERIOD):
    if daily_frame is None or len(daily_frame) < period + 1:
        return None
    high = daily_frame["High"]
    low = daily_frame["Low"]
    close = daily_frame["Close"]
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr_series = true_range.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    last_atr = atr_series.iloc[-1]
    if pd.isna(last_atr):
        return None
    return float(last_atr)

def calculate_initial_stop_loss(ma50_value, atr_value, multiplier=INITIAL_SL_ATR_MULTIPLIER):
    return float(ma50_value - (multiplier * atr_value))

def calculate_trailing_stop(highest_high, atr_value, multiplier=TRAILING_ATR_MULTIPLIER):
    return float(highest_high - (multiplier * atr_value))

def calculate_obv_series(daily_frame):
    if daily_frame is None or len(daily_frame) < 2:
        return None
    close = daily_frame["Close"]
    volume = daily_frame["Volume"]
    price_change = close.diff()
    direction = np.where(price_change > 0, 1, np.where(price_change < 0, -1, 0))
    obv_series = pd.Series(direction, index=daily_frame.index) * volume
    obv_series = obv_series.cumsum()
    return obv_series

def is_obv_above_average(daily_frame, period=OBV_MA_PERIOD):
    obv_series = calculate_obv_series(daily_frame)
    if obv_series is None or len(obv_series) < period:
        return False
    obv_ma_series = obv_series.rolling(window=period).mean()
    last_obv = obv_series.iloc[-1]
    last_obv_ma = obv_ma_series.iloc[-1]
    if pd.isna(last_obv_ma):
        return False
    return bool(last_obv > last_obv_ma)

def calculate_mfi(daily_frame, period=MFI_PERIOD):
    if daily_frame is None or len(daily_frame) < period + 1:
        return None
    typical_price = (daily_frame["High"] + daily_frame["Low"] + daily_frame["Close"]) / 3
    raw_money_flow = typical_price * daily_frame["Volume"]
    price_diff = typical_price.diff()
    positive_flow = raw_money_flow.where(price_diff > 0, 0.0)
    negative_flow = raw_money_flow.where(price_diff < 0, 0.0)
    positive_sum = positive_flow.rolling(window=period).sum()
    negative_sum = negative_flow.rolling(window=period).sum()
    last_positive = positive_sum.iloc[-1]
    last_negative = negative_sum.iloc[-1]
    if pd.isna(last_positive) or pd.isna(last_negative):
        return None
    if last_negative == 0:
        return 100.0
    money_flow_ratio = last_positive / last_negative
    mfi_value = 100 - (100 / (1 + money_flow_ratio))
    return float(mfi_value)

def calculate_cmf(daily_frame, period=CMF_PERIOD):
    if daily_frame is None or len(daily_frame) < period:
        return None
    high = daily_frame["High"]
    low = daily_frame["Low"]
    close = daily_frame["Close"]
    volume = daily_frame["Volume"]
    price_range = (high - low).replace(0, np.nan)
    money_flow_multiplier = ((close - low) - (high - close)) / price_range
    money_flow_multiplier = money_flow_multiplier.fillna(0)
    money_flow_volume = money_flow_multiplier * volume
    sum_mfv = money_flow_volume.rolling(window=period).sum()
    sum_volume = volume.rolling(window=period).sum()
    last_sum_mfv = sum_mfv.iloc[-1]
    last_sum_volume = sum_volume.iloc[-1]
    if pd.isna(last_sum_mfv) or pd.isna(last_sum_volume) or last_sum_volume == 0:
        return None
    return float(last_sum_mfv / last_sum_volume)

def calculate_vwap(daily_frame, period=VWAP_PERIOD):
    if daily_frame is None or len(daily_frame) < period:
        return None
    typical_price = (daily_frame["High"] + daily_frame["Low"] + daily_frame["Close"]) / 3
    volume = daily_frame["Volume"]
    recent_price = typical_price.tail(period)
    recent_volume = volume.tail(period)
    total_volume = recent_volume.sum()
    if total_volume == 0:
        return None
    vwap_value = (recent_price * recent_volume).sum() / total_volume
    return float(vwap_value)

def evaluate_whale_signal(daily_frame):
    close_price = float(daily_frame["Close"].iloc[-1])
    vwap_value = calculate_vwap(daily_frame)
    cmf_value = calculate_cmf(daily_frame)
    mfi_value = calculate_mfi(daily_frame)
    obv_above_average = is_obv_above_average(daily_frame)
    above_vwap = vwap_value is not None and close_price > vwap_value
    cmf_positive = cmf_value is not None and cmf_value > 0
    mfi_healthy = mfi_value is not None and MFI_HEALTHY_MIN < mfi_value < MFI_HEALTHY_MAX
    is_valid = above_vwap and cmf_positive and mfi_healthy and obv_above_average
    return {
        "is_valid": is_valid,
        "vwap_value": round(vwap_value, 2) if vwap_value is not None else None,
        "above_vwap": above_vwap,
        "cmf_value": round(cmf_value, 4) if cmf_value is not None else None,
        "cmf_positive": cmf_positive,
        "mfi_value": round(mfi_value, 2) if mfi_value is not None else None,
        "mfi_healthy": mfi_healthy,
        "obv_above_average": obv_above_average
    }

def resample_to_weekly(daily_frame):
    if daily_frame is None or daily_frame.empty:
        return None
    weekly_frame = daily_frame.resample("W").agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum"
    })
    weekly_frame = weekly_frame.dropna()
    return weekly_frame

def is_above_weekly_ma(daily_frame, period=WEEKLY_MA_PERIOD):
    weekly_frame = resample_to_weekly(daily_frame)
    if weekly_frame is None or len(weekly_frame) < period:
        return False
    weekly_ma = calculate_moving_average(weekly_frame, period)
    if weekly_ma is None:
        return False
    weekly_close = float(weekly_frame["Close"].iloc[-1])
    return weekly_close > weekly_ma

# Kerangka MA/EMA (dari catatan kelas): tangga 6 garis dari yang paling sensitif
# (MA5) sampai paling struktural (EMA200). "sma"/"ema" nentuin cara hitungnya,
# urutan list ini juga nentuin urutan dari paling dangkal ke paling dalam.
TREND_STRUCTURE_LEVELS = [
    ("MA5", "sma", 5),
    ("MA10", "sma", 10),
    ("MA20", "sma", 20),
    ("EMA50", "ema", 50),
    ("EMA100", "ema", 100),
    ("EMA200", "ema", 200),
]

def calculate_ema(daily_frame, period):
    if daily_frame is None or len(daily_frame) < period:
        return None
    ema_series = daily_frame["Close"].ewm(span=period, adjust=False, min_periods=period).mean()
    last_ema = ema_series.iloc[-1]
    if pd.isna(last_ema):
        return None
    return float(last_ema)

def evaluate_trend_structure(daily_frame):
    # Ngembaliin posisi harga terhadap seluruh tangga MA/EMA sekaligus, bukan cuma
    # satu garis kayak rule lama. Belum dipakai buat mutusin entry di mana pun --
    # ini cuma "bahan baku" buat sistem poin nanti.
    if daily_frame is None or daily_frame.empty:
        return None
    close_price = float(daily_frame["Close"].iloc[-1])
    levels = {}
    for name, kind, period in TREND_STRUCTURE_LEVELS:
        if kind == "sma":
            levels[name] = calculate_moving_average(daily_frame, period)
        else:
            levels[name] = calculate_ema(daily_frame, period)
    if any(value is None for value in levels.values()):
        return None
    price_above = {name: close_price > levels[name] for name, _, _ in TREND_STRUCTURE_LEVELS}
    ordered_values = [levels[name] for name, _, _ in TREND_STRUCTURE_LEVELS]
    bullish_alignment = all(ordered_values[i] > ordered_values[i + 1] for i in range(len(ordered_values) - 1))
    count_above = sum(1 for is_above in price_above.values() if is_above)
    # Garis paling dalam yang masih "ditembus" (harga close di bawahnya).
    # None kalau harga di atas semua garis (gak lagi pullback sama sekali).
    deepest_level_touched = None
    for name, _, _ in TREND_STRUCTURE_LEVELS:
        if not price_above[name]:
            deepest_level_touched = name
    return {
        "close_price": round(close_price, 2),
        "levels": {name: round(value, 2) for name, value in levels.items()},
        "price_above": price_above,
        "bullish_alignment": bullish_alignment,
        "count_above": count_above,
        "deepest_level_touched": deepest_level_touched
    }