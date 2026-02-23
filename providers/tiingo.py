"""Tiingo — historical EOD prices, IEX real-time.

Requires TIINGO_API_KEY.
"""

import os
from datetime import datetime, timedelta
import requests
from langchain.tools import Tool

API_KEY = os.getenv("TIINGO_API_KEY")
BASE_URL = "https://api.tiingo.com"


def query_tiingo(query: str) -> str:
    """Fetch historical prices and metadata from Tiingo.

    Query should be a stock ticker symbol like AAPL.
    """
    symbol = query.strip().upper().split()[0]
    headers = {"Content-Type": "application/json", "Authorization": f"Token {API_KEY}"}

    try:
        # Metadata
        meta = requests.get(f"{BASE_URL}/tiingo/daily/{symbol}", headers=headers, timeout=10).json()
        lines = [f"Tiingo data for {symbol}:"]
        lines.append(f"  Name: {meta.get('name', 'N/A')}")
        lines.append(f"  Exchange: {meta.get('exchangeCode', 'N/A')}")
        lines.append(f"  Start Date: {meta.get('startDate', 'N/A')}")
        lines.append(f"  Description: {str(meta.get('description', ''))[:200]}")

        # Recent prices (last 5 trading days)
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        prices = requests.get(
            f"{BASE_URL}/tiingo/daily/{symbol}/prices",
            headers=headers,
            params={"startDate": start, "endDate": end},
            timeout=10,
        ).json()

        if prices and isinstance(prices, list):
            lines.append(f"\nRecent prices (last {min(len(prices), 5)} days):")
            for p in prices[-5:]:
                date = p["date"][:10]
                lines.append(
                    f"  {date}: Open={p.get('adjOpen', 'N/A'):.2f} "
                    f"High={p.get('adjHigh', 'N/A'):.2f} "
                    f"Low={p.get('adjLow', 'N/A'):.2f} "
                    f"Close={p.get('adjClose', 'N/A'):.2f} "
                    f"Vol={p.get('adjVolume', 'N/A')}"
                )

        return "\n".join(lines)
    except Exception as e:
        return f"Tiingo error for {symbol}: {e}"


tool = None
if API_KEY:
    tool = Tool(
        name="tiingo",
        func=query_tiingo,
        description=(
            "Fetch historical EOD prices and stock metadata from Tiingo. "
            "Input should be a stock ticker symbol like AAPL, TSLA. "
            "Good for adjusted historical prices and basic stock info."
        ),
    )
