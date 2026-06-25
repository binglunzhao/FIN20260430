"""
Price data layer — wraps yfinance for OHLCV fetches.
Validated in research/issue_14_yfinance_ohlcv.py.
"""

import time
import yfinance as yf
import pandas as pd
from typing import List


def fetch_weekly_prices(tickers: List[str]) -> pd.DataFrame:
    """
    Download last 5 trading days of close prices for all tickers in one call.
    Returns a DataFrame with tickers as columns, dates as index.
    Falls back to per-ticker retry for any all-NaN columns (SQLite cache lock).
    """
    data = yf.download(tickers, period="5d", interval="1d",
                       auto_adjust=True, progress=False)
    close = data["Close"]

    # Retry any ticker that returned all-NaN (SQLite cache lock on first run)
    failed = close.columns[close.isna().all()].tolist()
    for ticker in failed:
        retry = yf.download(ticker, period="5d", interval="1d",
                            auto_adjust=True, progress=False)
        if not retry.empty:
            close[ticker] = retry["Close"]

    return close.dropna(axis=1, how="all").dropna(how="all")


def weekly_returns(close: pd.DataFrame) -> pd.Series:
    """Compute percentage change from Monday open to Friday close."""
    return ((close.iloc[-1] - close.iloc[0]) / close.iloc[0] * 100).round(2)


def fetch_next_earnings_dates(tickers: List[str]) -> dict:
    """
    Return {ticker: next_earnings_date} for each ticker using yfinance.
    Used by the scheduler to detect upcoming earnings events.
    """
    dates = {}
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).calendar
            if info is not None and "Earnings Date" in info:
                dates[ticker] = info["Earnings Date"]
        except Exception:
            dates[ticker] = None
        time.sleep(0.2)
    return dates
