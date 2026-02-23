"""Finnhub — real-time quotes, company news, sentiment.

Requires FINNHUB_API_KEY.
"""

import os
from datetime import datetime, timedelta
import requests
from langchain.tools import Tool

API_KEY = os.getenv("FINNHUB_API_KEY")
BASE_URL = "https://finnhub.io/api/v1"


def query_finnhub(query: str) -> str:
    """Fetch real-time quote and recent news from Finnhub.

    Query should be a stock ticker symbol like AAPL.
    """
    symbol = query.strip().upper().split()[0]
    headers = {"X-Finnhub-Token": API_KEY}

    try:
        # Real-time quote
        quote = requests.get(f"{BASE_URL}/quote", params={"symbol": symbol}, headers=headers, timeout=10).json()
        lines = [f"Finnhub data for {symbol}:"]
        lines.append(f"  Current: ${quote.get('c', 'N/A')}")
        lines.append(f"  Open: ${quote.get('o', 'N/A')}")
        lines.append(f"  High: ${quote.get('h', 'N/A')}")
        lines.append(f"  Low: ${quote.get('l', 'N/A')}")
        lines.append(f"  Prev Close: ${quote.get('pc', 'N/A')}")
        change = quote.get('dp', 0)
        lines.append(f"  Change: {change}%")

        # Recent news (last 7 days)
        today = datetime.now().strftime("%Y-%m-%d")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        news = requests.get(
            f"{BASE_URL}/company-news",
            params={"symbol": symbol, "from": week_ago, "to": today},
            headers=headers,
            timeout=10,
        ).json()

        if news and isinstance(news, list):
            lines.append(f"\nRecent news ({min(len(news), 3)} headlines):")
            for article in news[:3]:
                lines.append(f"  - {article.get('headline', 'N/A')} ({article.get('source', '')})")

        return "\n".join(lines)
    except Exception as e:
        return f"Finnhub error for {symbol}: {e}"


tool = None
if API_KEY:
    tool = Tool(
        name="finnhub",
        func=query_finnhub,
        description=(
            "Fetch real-time stock quotes and recent company news from Finnhub. "
            "Input should be a stock ticker symbol like AAPL, TSLA. Good for current price and news sentiment."
        ),
    )
