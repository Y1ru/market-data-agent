"""Financial Modeling Prep — fundamentals, earnings, financial statements.

Requires FMP_API_KEY.
"""

import os
import requests
from langchain.tools import Tool

API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/stable"


def query_fmp(query: str) -> str:
    """Fetch fundamentals and earnings from Financial Modeling Prep.

    Query format: 'SYMBOL' for company profile, or 'SYMBOL earnings' for earnings data.
    """
    parts = query.strip().split()
    symbol = parts[0].upper()
    mode = parts[1].lower() if len(parts) > 1 else "profile"

    try:
        if mode == "earnings":
            resp = requests.get(
                f"{BASE_URL}/income-statement",
                params={"symbol": symbol, "apikey": API_KEY, "limit": 4},
                timeout=10,
            ).json()

            if not resp or isinstance(resp, dict):
                return f"No earnings data for {symbol}"

            lines = [f"FMP income statement for {symbol} (last 4 periods):"]
            for stmt in resp[:4]:
                lines.append(f"  {stmt.get('date', 'N/A')}:")
                lines.append(f"    Revenue: ${stmt.get('revenue', 0):,.0f}")
                lines.append(f"    Net Income: ${stmt.get('netIncome', 0):,.0f}")
                lines.append(f"    EPS: {stmt.get('eps', 'N/A')}")
                lines.append(f"    Gross Margin: {stmt.get('grossProfitRatio', 'N/A')}")
            return "\n".join(lines)

        # Company profile
        resp = requests.get(
            f"{BASE_URL}/profile",
            params={"symbol": symbol, "apikey": API_KEY},
            timeout=10,
        ).json()

        if not resp:
            return f"No FMP profile data for {symbol}"

        p = resp[0] if isinstance(resp, list) else resp
        lines = [f"FMP profile for {symbol}:"]
        lines.append(f"  Name: {p.get('companyName', 'N/A')}")
        lines.append(f"  Sector: {p.get('sector', 'N/A')}")
        lines.append(f"  Industry: {p.get('industry', 'N/A')}")
        lines.append(f"  Market Cap: ${p.get('mktCap', 0):,.0f}")
        lines.append(f"  Price: ${p.get('price', 'N/A')}")
        lines.append(f"  Beta: {p.get('beta', 'N/A')}")
        lines.append(f"  Avg Volume: {p.get('volAvg', 'N/A')}")
        lines.append(f"  DCF: {p.get('dcf', 'N/A')}")
        desc = p.get("description", "")
        if desc:
            lines.append(f"  Description: {desc[:200]}...")
        return "\n".join(lines)
    except Exception as e:
        return f"FMP error for {symbol}: {e}"


tool = None
if API_KEY:
    tool = Tool(
        name="financial_modeling_prep",
        func=query_fmp,
        description=(
            "Fetch company fundamentals, profiles, and earnings from Financial Modeling Prep. "
            "Input: 'SYMBOL' for company profile or 'SYMBOL earnings' for income statements. "
            "Good for fundamental analysis — revenue, net income, EPS, market cap, DCF."
        ),
    )
