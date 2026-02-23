"""Binance — crypto spot prices, klines, order book.

Public endpoints, no API key needed.
"""

import requests
from langchain.tools import Tool

# Use binance.us for US-based users; fall back to binance.com for others
BASE_URLS = [
    "https://api.binance.us/api/v3",
    "https://api.binance.com/api/v3",
]


def query_binance(query: str) -> str:
    """Fetch crypto data from Binance.

    Query should be a trading pair like 'BTCUSDT' or just a symbol like 'BTC'
    (USDT is appended automatically).
    """
    symbol = query.strip().upper().replace("/", "").replace("-", "")
    if not symbol.endswith("USDT"):
        symbol = symbol + "USDT"

    # Try each base URL (binance.us first for US users)
    for base_url in BASE_URLS:
        try:
            ticker = requests.get(f"{base_url}/ticker/24hr", params={"symbol": symbol}, timeout=10).json()
            if "code" in ticker or "msg" in ticker:
                continue

            lines = [f"Binance data for {symbol}:"]
            lines.append(f"  Last Price: ${ticker['lastPrice']}")
            lines.append(f"  24h High: ${ticker['highPrice']}")
            lines.append(f"  24h Low: ${ticker['lowPrice']}")
            lines.append(f"  24h Change: {ticker['priceChangePercent']}%")
            lines.append(f"  24h Volume: {ticker['volume']} {symbol.replace('USDT', '')}")
            lines.append(f"  24h Quote Volume: ${float(ticker['quoteVolume']):,.0f} USDT")

            klines = requests.get(
                f"{base_url}/klines",
                params={"symbol": symbol, "interval": "1d", "limit": 5},
                timeout=10,
            ).json()

            if klines and isinstance(klines, list):
                lines.append("\nDaily candles (last 5):")
                for k in klines:
                    from datetime import datetime
                    ts = datetime.fromtimestamp(k[0] / 1000).strftime("%Y-%m-%d")
                    lines.append(f"  {ts}: O={float(k[1]):.2f} H={float(k[2]):.2f} L={float(k[3]):.2f} C={float(k[4]):.2f}")

            return "\n".join(lines)
        except requests.RequestException:
            continue

    return f"Binance error for {symbol}: all endpoints unreachable. Try e.g. 'BTC', 'ETH', 'SOL'."


tool = Tool(
    name="binance",
    func=query_binance,
    description=(
        "Fetch crypto spot prices, 24h stats, and daily candles from Binance. "
        "Input should be a crypto symbol like 'BTC', 'ETH', 'SOL' (USDT pair assumed). "
        "Free, no API key needed. Best for crypto, not stocks."
    ),
)
