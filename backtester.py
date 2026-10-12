import sys
import yfinance as yf
import pandas as pd

import stock_data

SECOND_LINER_UNIVERSE = ['AALI.JK', 'ACES.JK', 'ADES.JK', 'AKRA.JK', 'ANTM.JK', 'APIC.JK', 'APLN.JK', 'ARTO.JK', 'ASGR.JK', 'ASSA.JK', 'AUTO.JK', 'BAPA.JK', 'BBKP.JK', 'BBRM.JK', 'BBTN.JK', 'BBYB.JK', 'BDMN.JK', 'BFIN.JK', 'BIPI.JK', 'BIRD.JK', 'BJTM.JK', 'BKSL.JK', 'BMTR.JK', 'BNBR.JK', 'BNGA.JK', 'BRMS.JK', 'BRPT.JK', 'BSDE.JK', 'BSSR.JK', 'BULL.JK', 'BUMI.JK', 'BUVA.JK', 'BWPT.JK', 'CFIN.JK', 'CTRA.JK', 'CTTH.JK', 'DEFI.JK', 'DEWA.JK', 'DKFT.JK', 'DMAS.JK', 'DSNG.JK', 'DSSA.JK', 'ELSA.JK', 'ELTY.JK', 'EMTK.JK', 'ENRG.JK', 'ERAA.JK', 'ESSA.JK', 'EXCL.JK', 'FORU.JK', 'GGRM.JK', 'GIAA.JK', 'GJTL.JK', 'GPRA.JK', 'HMSP.JK', 'HRUM.JK', 'IATA.JK', 'ICON.JK', 'IMPC.JK', 'INCO.JK', 'INDF.JK', 'INDY.JK', 'INKP.JK', 'INTP.JK', 'ISAT.JK', 'ITMG.JK', 'JPFA.JK', 'JSMR.JK', 'KIJA.JK', 'KPIG.JK', 'LAPD.JK', 'LEAD.JK', 'LPKR.JK', 'LPPF.JK', 'LSIP.JK', 'MAPI.JK', 'MBSS.JK', 'MDIA.JK', 'MDKA.JK', 'MEDC.JK', 'MIDI.JK', 'MIKA.JK', 'MNCN.JK', 'MPMX.JK', 'MYOR.JK', 'NIKL.JK', 'NISP.JK', 'PADI.JK', 'PGAS.JK', 'PKPK.JK', 'PNBN.JK', 'PNLF.JK', 'PSAB.JK', 'PSKT.JK', 'PTBA.JK', 'PTRO.JK', 'PWON.JK', 'PYFA.JK', 'RAJA.JK', 'RBMS.JK', 'SCMA.JK', 'SDMU.JK', 'SIDO.JK', 'SIMP.JK', 'SMDR.JK', 'SMGR.JK', 'SMRA.JK', 'SMSM.JK', 'SOCI.JK', 'SRSN.JK', 'SRTG.JK', 'SSIA.JK', 'SSMS.JK', 'TBIG.JK', 'TINS.JK', 'TKIM.JK', 'TOBA.JK', 'TOTL.JK', 'TOWR.JK', 'TPIA.JK', 'ULTJ.JK', 'UNTR.JK', 'DPUM.JK', 'JGLE.JK', 'OASA.JK', 'POWR.JK', 'PRDA.JK', 'BRIS.JK', 'MINA.JK', 'HRTA.JK', 'MARK.JK', 'BELL.JK', 'KIOS.JK', 'GMFI.JK', 'PPRE.JK', 'MORA.JK', 'LCKM.JK', 'DFAM.JK', 'BTPS.JK', 'HEAL.JK', 'TUGU.JK', 'MSIN.JK', 'MAPA.JK', 'TCPI.JK', 'MGRO.JK', 'FILM.JK', 'LAND.JK', 'PANI.JK', 'YELO.JK', 'BEEF.JK', 'NATO.JK', 'COCO.JK', 'FUJI.JK', 'KOTA.JK', 'KEEN.JK', 'NZIA.JK', 'SINI.JK', 'ESIP.JK', 'INDO.JK', 'TRIN.JK', 'EPAC.JK', 'SGER.JK', 'BANK.JK', 'WMUU.JK', 'SNLK.JK', 'TAPG.JK', 'LUCY.JK', 'MGLV.JK', 'TRUE.JK', 'ARCI.JK', 'NICL.JK', 'UVCR.JK', 'BUKA.JK', 'OILS.JK', 'GPSO.JK', 'CMNT.JK', 'GTSI.JK', 'KUAS.JK', 'MTEL.JK', 'CMRY.JK', 'RMKE.JK', 'AVIA.JK', 'BSML.JK', 'ADMR.JK', 'NETV.JK', 'NTBK.JK', 'STAA.JK', 'WIRG.JK', 'ASHA.JK', 'ARKO.JK', 'DEWI.JK', 'KRYA.JK', 'HATM.JK', 'GULA.JK', 'JARR.JK', 'TOOL.JK', 'MEDS.JK', 'OMED.JK', 'ZATA.JK', 'MMIX.JK', 'PADA.JK', 'CBRE.JK', 'LAJU.JK', 'IRSX.JK', 'PACK.JK', 'PGEO.JK', 'FUTR.JK', 'BDKR.JK', 'PTMP.JK', 'CUAN.JK', 'NSSS.JK', 'JATI.JK', 'SMIL.JK', 'VKTR.JK', 'INET.JK', 'RMKO.JK', 'GRIA.JK', 'CYBR.JK', 'HUMI.JK', 'RSCH.JK', 'KOCI.JK', 'STRK.JK', 'KOKA.JK', 'UDNG.JK', 'RGAS.JK', 'AYAM.JK', 'UNTD.JK', 'MKAP.JK', 'BAIK.JK', 'VISI.JK', 'DATA.JK', 'NEST.JK', 'AADI.JK', 'RATU.JK', 'DGWG.JK', 'CBDK.JK', 'ASPR.JK', 'COIN.JK', 'CDIA.JK', 'KAQI.JK', 'FORE.JK', 'DKHH.JK', 'PIPA.JK', 'NCKL.JK', 'MBMA.JK', 'DOOH.JK', 'MSJA.JK', 'WIFI.JK', 'KETR.JK', 'EMAS.JK', 'RLCO.JK', 'SUPA.JK', 'WBSA.JK', 'JECX.JK', 'EMMI.JK', 'BACH.JK', 'ADRO.JK']

DEFAULT_LOOKBACK_PERIOD = "3y"
WARMUP_PERIOD = stock_data.MA_LONG_PERIOD
MAX_CONCURRENT_POSITIONS = 3
# Bobot dari ablation test: seberapa besar win rate anjlok pas tiap rule dimatiin
# (rule 5: -10.67 s/d -11.54pp, rule 3: -7.14pp, rule 4: -2pp tapi tail-risk gede).
# Rule 1+2 & rule 6 gak masuk skor -- dua-duanya kebukti gak nolak apa-apa yang
# berarti (rule 1+2: 0.0pp dua kali run; rule 6: efeknya ilang begitu rebutan
# slot dikontrol). Ini TITIK AWAL, bukan final -- masih perlu diuji ulang seiring
# data trade nambah banyak.
SCORE_WEIGHTS = {
    "squeeze": 3,
    "higher_low_bounce": 2,
    "accumulation": 4
}
MIN_SCORE_TO_ENTER = 6
REQUIRED_STOCK_DATA_ATTRIBUTES = [
    "calculate_atr",
    "calculate_moving_average",
    "is_liquid_enough",
    "evaluate_trend_structure",
    "is_volatility_squeeze",
    "is_higher_low_bounce",
    "evaluate_quiet_accumulation_signal",
    "calculate_initial_stop_loss",
    "calculate_trailing_stop",
    "is_above_weekly_ma",
    "extract_ticker_frame"
]

def verify_dependencies():
    missing_attributes = [name for name in REQUIRED_STOCK_DATA_ATTRIBUTES if not hasattr(stock_data, name)]
    if missing_attributes:
        print("File stock_data.py yang terpasang belum sesuai dengan backtester.py ini.")
        print("Fungsi berikut tidak ditemukan di stock_data.py:")
        for name in missing_attributes:
            print(f" - {name}")
        print("Silakan timpa stock_data.py Anda dengan versi terbaru sebelum menjalankan backtester.")
        return False
    return True

def fetch_backtest_data(ticker_codes, lookback_period=DEFAULT_LOOKBACK_PERIOD):
    tickers = [code if code.endswith(".JK") else f"{code}.JK" for code in ticker_codes]
    print(f"Mengunduh data historis {lookback_period} untuk {len(tickers)} saham second liner...")
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
            print("Peringatan: data yang diterima dari yfinance kosong. Cek koneksi internet atau rate limit.")
            return pd.DataFrame()
        print("Data historis berhasil diunduh.")
        return data
    except Exception as error:
        print(f"Gagal mengunduh data historis. Detail error: {error}")
        return pd.DataFrame()

def evaluate_entry_conditions(history_slice):
    # Sistem skor: rule 1+2 (trend structure) & rule 6 (filter mingguan) dihitung
    # & dicatat buat data, TAPI TIDAK menggagalkan entry -- kebukti dari ablation
    # test gak nolak apa-apa yang berarti. Yang jadi syarat cuma skor gabungan
    # squeeze + higher-low + akumulasi >= MIN_SCORE_TO_ENTER.
    result = {"is_valid": False, "score": 0}
    trend_structure = stock_data.evaluate_trend_structure(history_slice)
    if trend_structure is None:
        return result
    squeeze_pass = stock_data.is_volatility_squeeze(history_slice)
    higher_low_pass = stock_data.is_higher_low_bounce(history_slice)
    accumulation_signal = stock_data.evaluate_quiet_accumulation_signal(history_slice)
    accumulation_pass = accumulation_signal["is_valid"]
    score = 0
    if squeeze_pass:
        score += SCORE_WEIGHTS["squeeze"]
    if higher_low_pass:
        score += SCORE_WEIGHTS["higher_low_bounce"]
    if accumulation_pass:
        score += SCORE_WEIGHTS["accumulation"]
    result["score"] = score
    if score < MIN_SCORE_TO_ENTER:
        return result
    ma50_value = stock_data.calculate_moving_average(history_slice)
    atr_value = stock_data.calculate_atr(history_slice)
    if ma50_value is None or atr_value is None or atr_value <= 0:
        return result
    entry_price = float(history_slice["Close"].iloc[-1])
    initial_stop_loss = stock_data.calculate_initial_stop_loss(ma50_value, atr_value)
    if initial_stop_loss >= entry_price:
        return result
    weekly_filter_pass = stock_data.is_above_weekly_ma(history_slice)
    result.update({
        "is_valid": True,
        "entry_price": entry_price,
        "ma50_value": round(ma50_value, 2),
        "atr_value": round(atr_value, 2),
        "initial_stop_loss": round(initial_stop_loss, 2),
        "accumulation_signal": accumulation_signal,
        "trend_structure": trend_structure,
        "squeeze_pass": squeeze_pass,
        "higher_low_pass": higher_low_pass,
        "accumulation_pass": accumulation_pass,
        "weekly_filter_pass": weekly_filter_pass
    })
    return result

def finalize_exit_outcome(exit_date, exit_price, exit_reason, entry_price, partial_take_profit_triggered, partial_exit_date, partial_exit_price, partial_return_percentage):
    final_return_percentage = ((exit_price - entry_price) / entry_price) * 100
    if partial_take_profit_triggered:
        blended_return_percentage = (0.5 * partial_return_percentage) + (0.5 * final_return_percentage)
        combined_reason = f"Partial-Take-Profit + {exit_reason}"
    else:
        blended_return_percentage = final_return_percentage
        combined_reason = exit_reason
    return {
        "exit_date": exit_date,
        "exit_price": round(exit_price, 2),
        "exit_reason": combined_reason,
        "return_percentage": round(blended_return_percentage, 2),
        "partial_take_profit_triggered": partial_take_profit_triggered,
        "partial_exit_date": partial_exit_date,
        "partial_exit_price": partial_exit_price,
        "partial_return_percentage": partial_return_percentage
    }

def build_master_date_index(ticker_frames):
    all_dates = set()
    for frame in ticker_frames.values():
        all_dates.update(frame.index)
    return sorted(all_dates)

def build_date_position_maps(ticker_frames):
    position_maps = {}
    for ticker, frame in ticker_frames.items():
        position_maps[ticker] = {date: position for position, date in enumerate(frame.index)}
    return position_maps

def open_new_position(ticker, frame, position_index, entry_signal=None):
    history_slice = frame.iloc[:position_index + 1]
    if entry_signal is None:
        entry_signal = evaluate_entry_conditions(history_slice)
    if not entry_signal["is_valid"]:
        return None
    entry_price = entry_signal["entry_price"]
    entry_date = history_slice.index[-1]
    atr_value = entry_signal["atr_value"]
    initial_stop_loss = entry_signal["initial_stop_loss"]
    day_high = float(frame["High"].iloc[position_index])
    adtv_at_entry = stock_data.calculate_adtv(history_slice)
    trend_structure = entry_signal["trend_structure"]
    return {
        "ticker": ticker,
        "entry_date": entry_date,
        "entry_price": entry_price,
        "ma50_at_entry": entry_signal["ma50_value"],
        "atr_at_entry": atr_value,
        "initial_stop_loss": initial_stop_loss,
        "adtv_at_entry": adtv_at_entry,
        "deepest_level_at_entry": trend_structure["deepest_level_touched"],
        "count_above_at_entry": trend_structure["count_above"],
        "entry_score": entry_signal["score"],
        "vwap_at_entry": entry_signal["accumulation_signal"]["vwap_value"],
        "current_stop_level": initial_stop_loss,
        "highest_high_since_entry": day_high,
        "trailing_activated": False,
        "partial_take_profit_level": entry_price + (2.5 * atr_value),
        "partial_take_profit_triggered": False,
        "partial_exit_date": None,
        "partial_exit_price": None,
        "partial_return_percentage": None
    }

def build_trade_record(position, outcome):
    return {
        "ticker": position["ticker"],
        "entry_date": position["entry_date"],
        "entry_price": round(position["entry_price"], 2),
        "ma50_at_entry": position["ma50_at_entry"],
        "atr_at_entry": position["atr_at_entry"],
        "initial_stop_loss": position["initial_stop_loss"],
        "adtv_at_entry": position["adtv_at_entry"],
        "deepest_level_at_entry": position["deepest_level_at_entry"],
        "count_above_at_entry": position["count_above_at_entry"],
        "entry_score": position["entry_score"],
        "vwap_at_entry": position["vwap_at_entry"],
        "partial_take_profit_triggered": outcome["partial_take_profit_triggered"],
        "partial_exit_date": outcome["partial_exit_date"],
        "partial_exit_price": outcome["partial_exit_price"],
        "partial_return_percentage": outcome["partial_return_percentage"],
        "exit_date": outcome["exit_date"],
        "exit_price": outcome["exit_price"],
        "exit_reason": outcome["exit_reason"],
        "return_percentage": outcome["return_percentage"]
    }

def process_open_position(position, frame, position_index, current_date):
    day_low = float(frame["Low"].iloc[position_index])
    day_high = float(frame["High"].iloc[position_index])
    entry_price = position["entry_price"]
    if not position["partial_take_profit_triggered"] and day_high >= position["partial_take_profit_level"]:
        position["partial_take_profit_triggered"] = True
        position["partial_exit_date"] = current_date
        position["partial_exit_price"] = round(position["partial_take_profit_level"], 2)
        position["partial_return_percentage"] = round(((position["partial_take_profit_level"] - entry_price) / entry_price) * 100, 2)
    if day_low <= position["current_stop_level"]:
        exit_reason = "Trailing-Stop" if position["trailing_activated"] else "Initial-Stop-Loss"
        outcome = finalize_exit_outcome(current_date, position["current_stop_level"], exit_reason, entry_price, position["partial_take_profit_triggered"], position["partial_exit_date"], position["partial_exit_price"], position["partial_return_percentage"])
        return build_trade_record(position, outcome)
    if day_high > position["highest_high_since_entry"]:
        position["highest_high_since_entry"] = day_high
    if day_high > entry_price:
        position["trailing_activated"] = True
    if position["trailing_activated"]:
        history_slice = frame.iloc[:position_index + 1]
        atr_current = stock_data.calculate_atr(history_slice)
        if atr_current is not None and atr_current > 0:
            trailing_candidate = stock_data.calculate_trailing_stop(position["highest_high_since_entry"], atr_current)
            if trailing_candidate > position["current_stop_level"]:
                position["current_stop_level"] = trailing_candidate
    return None

def prepare_ticker_frames(ticker_codes, lookback_period=DEFAULT_LOOKBACK_PERIOD):
    # Dipisah dari simulasi biar data cuma di-download sekali, terus dipakai ulang
    # buat baseline + semua percobaan ablation (matiin rule satu-satu) tanpa
    # nge-hit yfinance berkali-kali.
    batch_data = fetch_backtest_data(ticker_codes, lookback_period)
    if batch_data.empty:
        return {}
    ticker_frames = {}
    for code in ticker_codes:
        frame = stock_data.extract_ticker_frame(batch_data, code)
        if frame is not None and len(frame) >= WARMUP_PERIOD + 1:
            ticker_frames[code] = frame
    return ticker_frames

def run_chronological_backtest(ticker_frames, max_concurrent_positions=None):
    concurrent_limit = max_concurrent_positions if max_concurrent_positions is not None else MAX_CONCURRENT_POSITIONS
    if not ticker_frames:
        print("Tidak ada saham dengan data historis yang cukup.")
        return [], calculate_performance_metrics([])
    print(f"Memulai simulasi kronologis untuk {len(ticker_frames)} saham dengan batas {concurrent_limit} posisi bersamaan (mode skor, ranking tiap hari)...")
    date_position_maps = build_date_position_maps(ticker_frames)
    master_dates = build_master_date_index(ticker_frames)
    open_positions = {}
    all_trades = []
    for current_date in master_dates:
        for ticker in list(open_positions.keys()):
            frame = ticker_frames[ticker]
            position_map = date_position_maps[ticker]
            if current_date not in position_map:
                continue
            position_index = position_map[current_date]
            position = open_positions[ticker]
            trade_record = process_open_position(position, frame, position_index, current_date)
            if trade_record is not None:
                all_trades.append(trade_record)
                del open_positions[ticker]
        available_slots = concurrent_limit - len(open_positions)
        if available_slots <= 0:
            continue
        candidates = []
        for ticker in ticker_frames:
            if ticker in open_positions:
                continue
            frame = ticker_frames[ticker]
            position_map = date_position_maps[ticker]
            if current_date not in position_map:
                continue
            position_index = position_map[current_date]
            if position_index < WARMUP_PERIOD:
                continue
            history_slice = frame.iloc[:position_index + 1]
            entry_signal = evaluate_entry_conditions(history_slice)
            if entry_signal["is_valid"]:
                candidates.append((ticker, frame, position_index, entry_signal))
        # Ranking: skor tertinggi duluan. Kalau kandidat lebih banyak dari slot
        # kosong, yang skornya lebih tinggi yang menang -- bukan siapa yang
        # ketemu duluan pas iterasi (beda dari versi lama).
        candidates.sort(key=lambda candidate: candidate[3]["score"], reverse=True)
        for ticker, frame, position_index, entry_signal in candidates[:available_slots]:
            new_position = open_new_position(ticker, frame, position_index, entry_signal)
            if new_position is not None:
                open_positions[ticker] = new_position
    for ticker, position in open_positions.items():
        frame = ticker_frames[ticker]
        final_close_price = float(frame["Close"].iloc[-1])
        final_date = frame.index[-1]
        outcome = finalize_exit_outcome(final_date, final_close_price, "End-Of-Data", position["entry_price"], position["partial_take_profit_triggered"], position["partial_exit_date"], position["partial_exit_price"], position["partial_return_percentage"])
        all_trades.append(build_trade_record(position, outcome))
    all_trades.sort(key=lambda trade: trade["entry_date"])
    print(f"Simulasi selesai. Total sinyal terkumpul: {len(all_trades)}.")
    metrics = calculate_performance_metrics(all_trades)
    return all_trades, metrics

def calculate_performance_metrics(trades):
    if not trades:
        return {
            "total_trades": 0,
            "win_rate": 0,
            "total_return_percentage": 0,
            "max_drawdown_percentage": 0
        }
    total_trades = len(trades)
    winning_trades = [trade for trade in trades if trade["return_percentage"] > 0]
    win_rate = (len(winning_trades) / total_trades) * 100
    # Tiap trade dianggap cuma pakai porsi 1/MAX_CONCURRENT_POSITIONS dari modal,
    # bukan 100% -- soalnya strategi ini bisa pegang sampai 3 posisi bersamaan.
    # Ini pendekatan kasar (belum ngitung modal yang lagi nganggur kalau slot
    # gak penuh 3), tapi cukup buat nyegah total_return_percentage meledak
    # eksponensial cuma gara-gara jumlah trade banyak, bukan karena kualitasnya
    # beneran lebih baik.
    running_equity = 100.0
    equity_curve = []
    for trade in trades:
        position_weighted_return = trade["return_percentage"] / MAX_CONCURRENT_POSITIONS
        running_equity = running_equity * (1 + (position_weighted_return / 100))
        equity_curve.append(running_equity)
    peak = equity_curve[0]
    max_drawdown = 0.0
    for value in equity_curve:
        if value > peak:
            peak = value
        drawdown = ((peak - value) / peak) * 100
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    total_return_percentage = equity_curve[-1] - 100.0
    return {
        "total_trades": total_trades,
        "win_rate": round(win_rate, 2),
        "total_return_percentage": round(total_return_percentage, 2),
        "max_drawdown_percentage": round(max_drawdown, 2)
    }

def summarize_by_liquidity(trades):
    # Membagi trade jadi dua kelompok berdasarkan ADTV di titik entry (median split
    # di antara trade yang lolos filter, bukan median seluruh universe), lalu
    # membandingkan performa dua kelompok itu. Ini buat menguji dugaan: apakah
    # entry di saham yang lagi sepi (sebelum ramai) hasilnya beda dibanding yang
    # udah ramai duluan.
    trades_with_adtv = [trade for trade in trades if trade.get("adtv_at_entry") is not None]
    if len(trades_with_adtv) < 4:
        return None
    sorted_trades = sorted(trades_with_adtv, key=lambda trade: trade["adtv_at_entry"])
    midpoint = len(sorted_trades) // 2
    quieter_group = sorted_trades[:midpoint]
    busier_group = sorted_trades[midpoint:]
    return {
        "quieter_half": {
            "metrics": calculate_performance_metrics(quieter_group),
            "adtv_range": (round(quieter_group[0]["adtv_at_entry"]), round(quieter_group[-1]["adtv_at_entry"])),
            "trades": sorted(quieter_group, key=lambda trade: trade["return_percentage"], reverse=True)
        },
        "busier_half": {
            "metrics": calculate_performance_metrics(busier_group),
            "adtv_range": (round(busier_group[0]["adtv_at_entry"]), round(busier_group[-1]["adtv_at_entry"])),
            "trades": sorted(busier_group, key=lambda trade: trade["return_percentage"], reverse=True)
        }
    }

def print_liquidity_group_trades(label, group):
    print(f"  Rincian trade ({label}), diurutkan dari return tertinggi:")
    for trade in group["trades"]:
        entry_date = str(trade["entry_date"])[:10]
        print(f"    {trade['ticker']:<10} | Entry {entry_date} | Return {trade['return_percentage']:>7.2f}% | ADTV Rp{round(trade['adtv_at_entry']):,}")

def summarize_exit_reasons(trades):
    counts = {}
    for trade in trades:
        reason = trade["exit_reason"]
        counts[reason] = counts.get(reason, 0) + 1
    return counts

def summarize_score_effectiveness(trades):
    # Validasi cepat: apa skor lebih tinggi beneran korelasi sama win rate lebih
    # tinggi? Kalau enggak, itu tanda bobotnya perlu diuji ulang.
    if not trades:
        return None
    scores = sorted(set(trade["entry_score"] for trade in trades), reverse=True)
    breakdown = {}
    for score in scores:
        group = [trade for trade in trades if trade["entry_score"] == score]
        wins = sum(1 for trade in group if trade["return_percentage"] > 0)
        breakdown[score] = {
            "count": len(group),
            "win_rate": round((wins / len(group)) * 100, 2) if group else 0
        }
    return breakdown

def print_summary(ticker_codes, trades, metrics):
    print("")
    print("========================================")
    print("RINGKASAN BACKTEST KRONOLOGIS DENGAN RISK LIMIT")
    print("========================================")
    print(f"Jumlah Saham Diuji     : {len(ticker_codes)}")
    print(f"Maks Posisi Bersamaan  : {MAX_CONCURRENT_POSITIONS}")
    print(f"Skor Minimal Masuk     : {MIN_SCORE_TO_ENTER} (bobot: squeeze={SCORE_WEIGHTS['squeeze']}, higher_low={SCORE_WEIGHTS['higher_low_bounce']}, akumulasi={SCORE_WEIGHTS['accumulation']}, maks={sum(SCORE_WEIGHTS.values())})")
    print(f"Total Perdagangan      : {metrics['total_trades']}")
    print(f"Win Rate               : {metrics['win_rate']}%")
    print(f"Total Profit/Loss      : {metrics['total_return_percentage']}%")
    print(f"Maximum Drawdown       : {metrics['max_drawdown_percentage']}%")
    exit_reason_counts = summarize_exit_reasons(trades)
    if exit_reason_counts:
        print("Rincian Alasan Keluar Posisi:")
        for reason, count in exit_reason_counts.items():
            print(f" - {reason}: {count}")
    print("========================================")
    score_breakdown = summarize_score_effectiveness(trades)
    if score_breakdown:
        print("SEBARAN SKOR ENTRY vs WIN RATE")
        print("(kalau skor tinggi gak korelasi sama win rate tinggi, bobotnya perlu diuji ulang)")
        print("----------------------------------------")
        for score in sorted(score_breakdown.keys(), reverse=True):
            info = score_breakdown[score]
            print(f"Skor {score}: {info['count']} trade, win rate {info['win_rate']}%")
        print("========================================")
    liquidity_breakdown = summarize_by_liquidity(trades)
    if liquidity_breakdown:
        print("PERBANDINGAN: SAHAM SEPI vs SAHAM RAMAI SAAT ENTRY")
        print("(dibagi median ADTV di antara trade yang lolos, bukan seluruh universe)")
        print("----------------------------------------")
        quieter = liquidity_breakdown["quieter_half"]
        busier = liquidity_breakdown["busier_half"]
        print(f"Kelompok Lebih Sepi   | ADTV Rp{quieter['adtv_range'][0]:,} - Rp{quieter['adtv_range'][1]:,}")
        print(f"  Total Trade         : {quieter['metrics']['total_trades']}")
        print(f"  Win Rate            : {quieter['metrics']['win_rate']}%")
        print(f"  Total Return        : {quieter['metrics']['total_return_percentage']}%")
        print_liquidity_group_trades("Lebih Sepi", quieter)
        print("----------------------------------------")
        print(f"Kelompok Lebih Ramai  | ADTV Rp{busier['adtv_range'][0]:,} - Rp{busier['adtv_range'][1]:,}")
        print(f"  Total Trade         : {busier['metrics']['total_trades']}")
        print(f"  Win Rate            : {busier['metrics']['win_rate']}%")
        print(f"  Total Return        : {busier['metrics']['total_return_percentage']}%")
        print_liquidity_group_trades("Lebih Ramai", busier)
        print("========================================")
    else:
        print("Belum cukup data buat bandingin sepi vs ramai (minimal butuh 4 trade dengan data ADTV).")
        print("========================================")

def main():
    print("BACKTESTER KRONOLOGIS DENGAN PORTFOLIO RISK LIMIT - MULAI EKSEKUSI")
    if not verify_dependencies():
        sys.exit(1)
    ticker_frames = prepare_ticker_frames(SECOND_LINER_UNIVERSE, DEFAULT_LOOKBACK_PERIOD)
    trades, metrics = run_chronological_backtest(ticker_frames)
    print_summary(SECOND_LINER_UNIVERSE, trades, metrics)
    return trades, metrics

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Program berhenti karena error tak terduga: {error}")
        sys.exit(1)