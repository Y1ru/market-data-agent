"""CoinGecko — crypto prices, market cap, trending coins.

Free, no API key required.
"""

import requests
from langchain.tools import Tool

BASE_URL = "https://api.coingecko.com/api/v3"

# Map common symbols to CoinGecko IDs
COIN_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "ADA": "cardano",
    "DOT": "polkadot",
    "DOGE": "dogecoin",
    "XRP": "ripple",
    "AVAX": "avalanche-2",
    "MATIC": "matic-network",
    "LINK": "chainlink",
    "UNI": "uniswap",
    "ATOM": "cosmos",
    "LTC": "litecoin",
    "BNB": "binancecoin",
    "SHIB": "shiba-inu",
}


def query_coingecko(query: str) -> str:
    """Fetch crypto data from CoinGecko.

    Query can be a symbol (BTC, ETH) or CoinGecko ID (bitcoin, ethereum),
    or 'trending' to see trending coins.
    """
    q = query.strip().upper()

    try:
        if q == "TRENDING":
            resp = requests.get(f"{BASE_URL}/search/trending", timeout=10).json()
            coins = resp.get("coins", [])
            lines = ["CoinGecko trending coins:"]
            for item in coins[:10]:
                c = item.get("item", {})
                lines.append(
                    f"  #{c.get('market_cap_rank', '?')} {c.get('name', '')} ({c.get('symbol', '')}) "
                    f"— Price BTC: {c.get('price_btc', 'N/A'):.8f}"
                )
            return "\n".join(lines)

        # Resolve symbol to ID
        coin_id = COIN_MAP.get(q, q.lower())

        resp = requests.get(
            f"{BASE_URL}/coins/{coin_id}",
            params={"localization": "false", "tickers": "false", "community_data": "false", "developer_data": "false"},
            timeout=10,
        ).json()

        if "error" in resp:
            return f"CoinGecko: coin '{coin_id}' not found. Try 'BTC', 'ETH', 'SOL', or 'trending'."

        market = resp.get("market_data", {})
        lines = [f"CoinGecko data for {resp.get('name', coin_id)} ({resp.get('symbol', '').upper()}):"]
        lines.append(f"  Price: ${market.get('current_price', {}).get('usd', 'N/A'):,.2f}")
        lines.append(f"  Market Cap: ${market.get('market_cap', {}).get('usd', 0):,.0f}")
        lines.append(f"  24h Volume: ${market.get('total_volume', {}).get('usd', 0):,.0f}")
        lines.append(f"  24h Change: {market.get('price_change_percentage_24h', 'N/A')}%")
        lines.append(f"  7d Change: {market.get('price_change_percentage_7d', 'N/A')}%")
        lines.append(f"  30d Change: {market.get('price_change_percentage_30d', 'N/A')}%")
        lines.append(f"  ATH: ${market.get('ath', {}).get('usd', 'N/A'):,.2f}")
        lines.append(f"  ATH Change: {market.get('ath_change_percentage', {}).get('usd', 'N/A')}%")
        lines.append(f"  Market Cap Rank: #{resp.get('market_cap_rank', 'N/A')}")

        return "\n".join(lines)
    except Exception as e:
        return f"CoinGecko error: {e}"


tool = Tool(
    name="coingecko",
    func=query_coingecko,
    description=(
        "Fetch crypto prices, market cap, volume, and trends from CoinGecko. "
        "Input: crypto symbol (BTC, ETH, SOL) or 'trending' for top trending coins. "
        "Free, no API key needed. Best for crypto overview and market cap data."
    ),
)
