"""Polygon.io — aggregates, tick data, options.

Requires POLYGON_API_KEY.
"""

import os
from datetime import datetime, timedelta
import requests
from langchain.tools import Tool

API_KEY = os.getenv("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io"


def query_polygon(query: str) -> str:
    """Fetch aggregate price data from Polygon.io.

    Query should be a stock ticker symbol like AAPL.
    """
    symbol = query.strip().upper().split()[0]

    try:
        # Last 5 trading days of daily aggregates
        today = datetime.now().strftime("%Y-%m-%d")
        week_ago = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        url = f"{BASE_URL}/v2/aggs/ticker/{symbol}/range/1/day/{week_ago}/{today}"
        resp = requests.get(url, params={"apiKey": API_KEY, "limit": 5, "sort": "desc"}, timeout=10).json()

        if resp.get("resultsCount", 0) == 0:
            return f"No Polygon data found for {symbol}"

        lines = [f"Polygon.io daily aggregates for {symbol}:"]
        for bar in resp.get("results", []):
            ts = datetime.fromtimestamp(bar["t"] / 1000).strftime("%Y-%m-%d")
            lines.append(
                f"  {ts}: Open={bar['o']:.2f} High={bar['h']:.2f} Low={bar['l']:.2f} "
                f"Close={bar['c']:.2f} Volume={bar['v']}"
            )

        # Ticker details
        details = requests.get(
            f"{BASE_URL}/v3/reference/tickers/{symbol}",
            params={"apiKey": API_KEY},
            timeout=10,
        ).json()
        result = details.get("results", {})
        if result:
            lines.append(f"\n  Name: {result.get('name', 'N/A')}")
            lines.append(f"  Market: {result.get('market', 'N/A')}")
            lines.append(f"  Locale: {result.get('locale', 'N/A')}")
            lines.append(f"  Primary Exchange: {result.get('primary_exchange', 'N/A')}")

        return "\n".join(lines)
    except Exception as e:
        return f"Polygon error for {symbol}: {e}"


tool = None
if API_KEY:
    tool = Tool(
        name="polygon",
        func=query_polygon,
        description=(
            "Fetch daily aggregate price bars and ticker details from Polygon.io. "
            "Input should be a stock ticker symbol like AAPL, TSLA. Good for OHLCV data and market info."
        ),
    )
