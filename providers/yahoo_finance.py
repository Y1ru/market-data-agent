"""Yahoo Finance — free, no API key required.

Uses Yahoo's public query endpoints for price history and key stats.
"""

import requests as _requests
from langchain.tools import Tool

_SESSION = _requests.Session()
_SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
})

_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
_QUOTE_URL = "https://query1.finance.yahoo.com/v6/finance/quote"


def query_yahoo_finance(query: str) -> str:
    """Fetch stock data from Yahoo Finance. Query should be a ticker symbol like AAPL."""
    symbol = query.strip().upper().split()[0]

    try:
        # v8 chart endpoint — reliable, includes price history + metadata
        resp = _SESSION.get(
            _CHART_URL.format(symbol=symbol),
            params={"range": "5d", "interval": "1d", "includePrePost": "false"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        result = data.get("chart", {}).get("result")
        if not result:
            return f"No Yahoo Finance data found for {symbol}"

        chart = result[0]
        meta = chart.get("meta", {})
        timestamps = chart.get("timestamp", [])
        quotes = chart.get("indicators", {}).get("quote", [{}])[0]

        lines = [f"Yahoo Finance data for {symbol}:"]
        lines.append(f"  Name: {meta.get('longName', meta.get('shortName', symbol))}")
        lines.append(f"  Current Price: {meta.get('regularMarketPrice', 'N/A')}")
        lines.append(f"  Previous Close: {meta.get('chartPreviousClose', 'N/A')}")
        lines.append(f"  52-Week High: {meta.get('fiftyTwoWeekHigh', 'N/A')}")
        lines.append(f"  52-Week Low: {meta.get('fiftyTwoWeekLow', 'N/A')}")
        lines.append(f"  50-Day Avg: {meta.get('fiftyDayAverage', 'N/A')}")
        lines.append(f"  200-Day Avg: {meta.get('twoHundredDayAverage', 'N/A')}")
        lines.append(f"  Exchange: {meta.get('exchangeName', 'N/A')}")
        lines.append(f"  Currency: {meta.get('currency', 'N/A')}")

        if timestamps:
            from datetime import datetime
            opens = quotes.get("open", [])
            highs = quotes.get("high", [])
            lows = quotes.get("low", [])
            closes = quotes.get("close", [])
            volumes = quotes.get("volume", [])

            lines.append("\nRecent price history (last 5 trading days):")
            for i, ts in enumerate(timestamps):
                date = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                o = f"{opens[i]:.2f}" if opens[i] else "N/A"
                h = f"{highs[i]:.2f}" if highs[i] else "N/A"
                l = f"{lows[i]:.2f}" if lows[i] else "N/A"
                c = f"{closes[i]:.2f}" if closes[i] else "N/A"
                v = str(int(volumes[i])) if volumes[i] else "N/A"
                lines.append(f"  {date}: Open={o} High={h} Low={l} Close={c} Vol={v}")

        return "\n".join(lines)
    except Exception as e:
        return f"Yahoo Finance error for {symbol}: {e}"


tool = Tool(
    name="yahoo_finance",
    func=query_yahoo_finance,
    description=(
        "Fetch stock price history, fundamentals, dividends, and key metrics from Yahoo Finance. "
        "Input should be a stock ticker symbol like AAPL, TSLA, MSFT. Free, no API key needed."
    ),
)
