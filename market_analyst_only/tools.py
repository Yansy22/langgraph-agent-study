import os
import pandas as pd
import yfinance as yf
from stockstats import wrap
from typing import Annotated
from langchain_core.tools import tool

# Minimalistic config import
from .config import get_config

def get_stock_data_raw(symbol: str, start_date: str, end_date: str):
    """Fetch raw stock data and cache it."""
    config = get_config()
    os.makedirs(config["data_cache_dir"], exist_ok=True)
    
    data_file = os.path.join(
        config["data_cache_dir"],
        f"{symbol}-data-{start_date}-{end_date}.csv",
    )

    if os.path.exists(data_file):
        data = pd.read_csv(data_file)
        data["Date"] = pd.to_datetime(data["Date"])
    else:
        # Standardize fetching to be simple
        data = yf.download(
            symbol,
            start=start_date,
            end=end_date,
            multi_level_index=False,
            progress=False,
            auto_adjust=True,
        )
        data = data.reset_index()
        data.to_csv(data_file, index=False)
    
    return data

@tool
def get_stock_data(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """Fetch candlestick stock price data for the company."""
    data = get_stock_data_raw(symbol, start_date, end_date)
    return f"# Stock data for {symbol.upper()} from {start_date} to {end_date}\n" + data.to_csv()

@tool
def get_indicators(
    symbol: Annotated[str, "ticker symbol for the company"],
    indicator: Annotated[str, "technical indicator like rsi, macd, boll"],
    curr_date: Annotated[str, "date for the indicator, YYYY-mm-dd"],
    look_back_days: Annotated[int, "number of days for analysis"] = 30,
) -> str:
    """Calculate and return technical indicators for the stock."""
    # Simplified approach: Look back enough to calculate stats
    end_dt = pd.to_datetime(curr_date)
    start_dt = end_dt - pd.DateOffset(days=look_back_days + 100) # buffer for SMA
    
    data = get_stock_data_raw(symbol, start_dt.strftime("%Y-%m-%d"), curr_date)
    
    df = wrap(data)
    df[indicator] # trigger calculation
    
    # Return formatted window of indicator values
    target_dt = end_dt - pd.DateOffset(days=look_back_days)
    mask = (df['Date'] >= target_dt) & (df['Date'] <= end_dt)
    window = df.loc[mask, ['Date', indicator]]
    
    return f"## {indicator} analysis for {symbol} up to {curr_date}\n" + window.to_csv(index=False)
