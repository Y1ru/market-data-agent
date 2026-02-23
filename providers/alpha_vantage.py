"""Alpha Vantage — technical indicators, forex, crypto.

Requires ALPHA_VANTAGE_API_KEY.
"""

import os
import requests
from langchain.tools import Tool

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"


def query_alpha_vantage(query: str) -> str:
    """Fetch technical indicators from Alpha Vantage.

    Query format: 'SYMBOL INDICATOR' e.g. 'AAPL RSI' or just 'AAPL' for overview.
    Supported indicators: RSI, SMA, EMA, MACD, BBANDS.
    """
    parts = query.strip().upper().split()
    symbol = parts[0]
    indicator = parts[1] if len(parts) > 1 else "OVERVIEW"

    try:
        if indicator == "OVERVIEW":
            params = {"function": "OVERVIEW", "symbol": symbol, "apikey": API_KEY}
            data = requests.get(BASE_URL, params=params, timeout=10).json()
            if "Symbol" not in data:
                return f"No overview data for {symbol}"
            lines = [f"Alpha Vantage overview for {symbol}:"]
            for key in ["Name", "Sector", "Industry", "MarketCapitalization", "PERatio", "EPS", "DividendYield", "52WeekHigh", "52WeekLow", "AnalystTargetPrice"]:
                lines.append(f"  {key}: {data.get(key, 'N/A')}")
            return "\n".join(lines)

        func_map = {
            "RSI": ("RSI", {"time_period": "14", "series_type": "close"}),
            "SMA": ("SMA", {"time_period": "20", "series_type": "close"}),
            "EMA": ("EMA", {"time_period": "20", "series_type": "close"}),
            "MACD": ("MACD", {"series_type": "close"}),
            "BBANDS": ("BBANDS", {"time_period": "20", "series_type": "close"}),
        }

        if indicator not in func_map:
            return f"Unknown indicator '{indicator}'. Supported: RSI, SMA, EMA, MACD, BBANDS, or omit for overview."

        func_name, extra_params = func_map[indicator]
        params = {"function": func_name, "symbol": symbol, "interval": "daily", "apikey": API_KEY, **extra_params}
        data = requests.get(BASE_URL, params=params, timeout=10).json()

        tech_key = [k for k in data if k.startswith("Technical Analysis")]
        if not tech_key:
            return f"No {indicator} data returned for {symbol}. Response: {list(data.keys())}"

        values = data[tech_key[0]]
        recent = list(values.items())[:5]
        lines = [f"Alpha Vantage {indicator} for {symbol} (last 5 data points):"]
        for date, vals in recent:
            formatted = ", ".join(f"{k}={v}" for k, v in vals.items())
            lines.append(f"  {date}: {formatted}")
        return "\n".join(lines)
    except Exception as e:
        return f"Alpha Vantage error: {e}"


tool = None
if API_KEY:
    tool = Tool(
        name="alpha_vantage",
        func=query_alpha_vantage,
        description=(
            "Fetch technical indicators (RSI, SMA, EMA, MACD, BBANDS) and company overview from Alpha Vantage. "
            "Input format: 'SYMBOL INDICATOR' e.g. 'AAPL RSI' or 'TSLA MACD'. Just a symbol gives an overview."
        ),
    )
