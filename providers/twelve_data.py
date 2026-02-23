"""Twelve Data — real-time, historical, 800+ technical indicators.

Requires TWELVE_DATA_API_KEY.
"""

import os
import requests
from langchain.tools import Tool

API_KEY = os.getenv("TWELVE_DATA_API_KEY")
BASE_URL = "https://api.twelvedata.com"


def query_twelve_data(query: str) -> str:
    """Fetch price data or technical indicators from Twelve Data.

    Query format: 'SYMBOL' for price, or 'SYMBOL INDICATOR' e.g. 'AAPL RSI'.
    Supported indicators: RSI, SMA, EMA, MACD, BBANDS, STOCH, ADX, ATR.
    """
    parts = query.strip().upper().split()
    symbol = parts[0]
    indicator = parts[1] if len(parts) > 1 else None

    try:
        if indicator:
            # Technical indicator
            indicator_map = {
                "RSI": "rsi",
                "SMA": "sma",
                "EMA": "ema",
                "MACD": "macd",
                "BBANDS": "bbands",
                "STOCH": "stoch",
                "ADX": "adx",
                "ATR": "atr",
            }
            ind = indicator_map.get(indicator)
            if not ind:
                return f"Unknown indicator '{indicator}'. Supported: {', '.join(indicator_map.keys())}"

            params = {"symbol": symbol, "interval": "1day", "apikey": API_KEY, "outputsize": 5}
            if ind in ("rsi", "sma", "ema", "atr", "adx"):
                params["time_period"] = 14
            resp = requests.get(f"{BASE_URL}/{ind}", params=params, timeout=10).json()

            if "values" not in resp:
                return f"No {indicator} data for {symbol}: {resp.get('message', 'unknown error')}"

            lines = [f"Twelve Data {indicator} for {symbol} (last 5):"]
            for v in resp["values"]:
                vals = ", ".join(f"{k}={v2}" for k, v2 in v.items() if k != "datetime")
                lines.append(f"  {v['datetime']}: {vals}")
            return "\n".join(lines)

        # Time series (price)
        params = {"symbol": symbol, "interval": "1day", "apikey": API_KEY, "outputsize": 5}
        resp = requests.get(f"{BASE_URL}/time_series", params=params, timeout=10).json()

        if "values" not in resp:
            return f"No price data for {symbol}: {resp.get('message', 'unknown error')}"

        lines = [f"Twelve Data prices for {symbol} (last 5 trading days):"]
        for v in resp["values"]:
            lines.append(f"  {v['datetime']}: O={v['open']} H={v['high']} L={v['low']} C={v['close']} V={v['volume']}")
        return "\n".join(lines)
    except Exception as e:
        return f"Twelve Data error: {e}"


tool = None
if API_KEY:
    tool = Tool(
        name="twelve_data",
        func=query_twelve_data,
        description=(
            "Fetch real-time/historical prices and technical indicators from Twelve Data. "
            "Input: 'SYMBOL' for price data or 'SYMBOL INDICATOR' for technicals. "
            "Indicators: RSI, SMA, EMA, MACD, BBANDS, STOCH, ADX, ATR. "
            "Example: 'AAPL RSI' or 'TSLA MACD'."
        ),
    )
