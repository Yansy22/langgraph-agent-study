import os
import pandas as pd
import yfinance as yf
from stockstats import wrap
from typing import Annotated, Dict, Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Internal utility from stockstats_utils.py
from .stockstats_utils import StockstatsUtils


# 특정 기간 동안의 야후 파이낸스(Yahoo Finance) 주식 데이터를 온라인에서 가져오는 함수
def get_YFin_data_online(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
):
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")

        # Create ticker object
        ticker = yf.Ticker(symbol.upper())

        # Fetch historical data for the specified date range
        data = ticker.history(start=start_date, end=end_date)

        # Check if data is empty
        if data.empty:
            return (
                f"No data found for symbol '{symbol}' between {start_date} and {end_date}"
            )

        # Remove timezone info from index for cleaner output
        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)

        # Round numerical values to 2 decimal places for cleaner display
        numeric_columns = ["Open", "High", "Low", "Close", "Adj Close"]
        for col in numeric_columns:
            if col in data.columns:
                data[col] = data[col].round(2)

        # Convert DataFrame to CSV string
        csv_string = data.to_csv()

        # Add header information
        header = f"# Stock data for {symbol.upper()} from {start_date} to {end_date}\n"
        header += f"# Total records: {len(data)}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        return header + csv_string
    except Exception as e:
        return f"Error fetching stock data: {str(e)}"

# 조회 기간 동안의 특정 기술적 지표 값을 가져와서 보고서 형식으로 반환하는 함수
def get_stock_stats_indicators_window(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[str, "The current trading date you are trading on, YYYY-mm-dd"],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:

    best_ind_params = {
        "close_50_sma": "50 SMA: A medium-term trend indicator.",
        "close_200_sma": "200 SMA: A long-term trend benchmark.",
        "close_10_ema": "10 EMA: A responsive short-term average.",
        "macd": "MACD: Momentum via differences of EMAs.",
        "macds": "MACD Signal: EMA smoothing of the MACD line.",
        "macdh": "MACD Histogram: Gap between MACD and signal.",
        "rsi": "RSI: Momentum overbought/oversold indicator.",
        "boll": "Bollinger Middle: 20 SMA.",
        "boll_ub": "Bollinger Upper Band.",
        "boll_lb": "Bollinger Lower Band.",
        "atr": "ATR: Measures volatility.",
        "vwma": "VWMA: Volume weighted average.",
        "mfi": "MFI: Money Flow Index.",
    }

    if indicator not in best_ind_params:
        return f"Indicator {indicator} is not supported. Supported: {list(best_ind_params.keys())}"

    end_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    start_date_dt = end_date_dt - relativedelta(days=look_back_days)

    try:
        indicator_data = _get_stock_stats_bulk(symbol, indicator, curr_date)
        
        current_dt = end_date_dt
        date_values = []
        
        while current_dt >= start_date_dt:
            date_str = current_dt.strftime('%Y-%m-%d')
            if date_str in indicator_data:
                indicator_value = indicator_data[date_str]
            else:
                indicator_value = "N/A"
            
            date_values.append((date_str, indicator_value))
            current_dt = current_dt - relativedelta(days=1)
        
        ind_string = "\n".join([f"{d}: {v}" for d, v in date_values])
        
    except Exception as e:
        print(f"Error getting bulk stockstats data: {e}")
        return f"Error calculating indicators: {str(e)}"

    result_str = (
        f"## {indicator} values from {start_date_dt.strftime('%Y-%m-%d')} to {curr_date}:\n\n"
        + ind_string
        + "\n\n"
        + best_ind_params.get(indicator, "")
    )

    return result_str


def _get_stock_stats_bulk(
    symbol: str,
    indicator: str,
    curr_date: str
) -> dict:
    # Local defaults
    data_cache_dir = os.getenv("DATA_CACHE_DIR", "data_cache")
    
    today_date = pd.Timestamp.today()
    end_date_str = today_date.strftime("%Y-%m-%d")
    start_date = today_date - pd.DateOffset(years=15)
    start_date_str = start_date.strftime("%Y-%m-%d")
    
    os.makedirs(data_cache_dir, exist_ok=True)
    
    data_file = os.path.join(
        data_cache_dir,
        f"{symbol}-YFin-bulk-{start_date_str}-{end_date_str}.csv",
    )
    
    if os.path.exists(data_file):
        data = pd.read_csv(data_file)
        data["Date"] = pd.to_datetime(data["Date"])
    else:
        data = yf.download(
            symbol,
            start=start_date_str,
            end=end_date_str,
            multi_level_index=False,
            progress=False,
            auto_adjust=True,
        )
        data = data.reset_index()
        data.to_csv(data_file, index=False)
    
    df = wrap(data)
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    
    # Calculate the indicator
    _ = df[indicator]
    
    result_dict = {}
    for _, row in df.iterrows():
        date_str = row["Date"]
        indicator_value = row[indicator]
        result_dict[date_str] = str(indicator_value) if not pd.isna(indicator_value) else "N/A"
    
    return result_dict


def get_fundamentals(ticker: str, curr_date: str = None):
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        info = ticker_obj.info
        if not info: return f"No fundamentals found for {ticker}"
        
        fields = ["longName", "sector", "industry", "marketCap", "trailingPE", "forwardPE", "dividendYield"]
        result = [f"{f}: {info.get(f)}" for f in fields if info.get(f) is not None]
        return f"# Fundamentals for {ticker.upper()}\n" + "\n".join(result)
    except Exception as e:
        return f"Error: {str(e)}"

def get_balance_sheet(ticker: str, freq: str = "quarterly"):
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        data = ticker_obj.quarterly_balance_sheet if freq == "quarterly" else ticker_obj.balance_sheet
        return data.to_csv() if not data.empty else "No data"
    except Exception as e: return f"Error: {str(e)}"

def get_cashflow(ticker: str, freq: str = "quarterly"):
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        data = ticker_obj.quarterly_cashflow if freq == "quarterly" else ticker_obj.cashflow
        return data.to_csv() if not data.empty else "No data"
    except Exception as e: return f"Error: {str(e)}"

def get_income_statement(ticker: str, freq: str = "quarterly"):
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        data = ticker_obj.quarterly_income_stmt if freq == "quarterly" else ticker_obj.income_stmt
        return data.to_csv() if not data.empty else "No data"
    except Exception as e: return f"Error: {str(e)}"

def get_insider_transactions(ticker: str):
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        data = ticker_obj.insider_transactions
        return data.to_csv() if data is not None and not data.empty else "No data"
    except Exception as e: return f"Error: {str(e)}"