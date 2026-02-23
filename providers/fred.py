"""FRED — Federal Reserve Economic Data.

Macro data: interest rates, CPI, GDP, unemployment.
Requires FRED_API_KEY.
"""

import os
import requests
from langchain.tools import Tool

API_KEY = os.getenv("FRED_API_KEY")
BASE_URL = "https://api.stlouisfed.org/fred"

# Common FRED series for quick lookup
SERIES_ALIASES = {
    "FEDERAL FUNDS RATE": "FEDFUNDS",
    "FED FUNDS": "FEDFUNDS",
    "INTEREST RATE": "FEDFUNDS",
    "CPI": "CPIAUCSL",
    "INFLATION": "CPIAUCSL",
    "GDP": "GDP",
    "UNEMPLOYMENT": "UNRATE",
    "UNEMPLOYMENT RATE": "UNRATE",
    "10 YEAR TREASURY": "DGS10",
    "TREASURY": "DGS10",
    "2 YEAR TREASURY": "DGS2",
    "MORTGAGE": "MORTGAGE30US",
    "30 YEAR MORTGAGE": "MORTGAGE30US",
    "M2": "M2SL",
    "MONEY SUPPLY": "M2SL",
}


def query_fred(query: str) -> str:
    """Fetch macroeconomic data from FRED.

    Query can be a FRED series ID (e.g. 'FEDFUNDS') or a keyword
    like 'CPI', 'GDP', 'unemployment', 'federal funds rate'.
    """
    q = query.strip().upper()
    series_id = SERIES_ALIASES.get(q, q.split()[0])

    try:
        # Get series info
        info_resp = requests.get(
            f"{BASE_URL}/series",
            params={"series_id": series_id, "api_key": API_KEY, "file_type": "json"},
            timeout=10,
        ).json()

        serieses = info_resp.get("seriess", [])
        if not serieses:
            return f"FRED series '{series_id}' not found. Try keywords like: CPI, GDP, unemployment, federal funds rate, treasury"

        meta = serieses[0]
        lines = [f"FRED data for {meta.get('title', series_id)} ({series_id}):"]
        lines.append(f"  Units: {meta.get('units', 'N/A')}")
        lines.append(f"  Frequency: {meta.get('frequency', 'N/A')}")

        # Get recent observations
        obs_resp = requests.get(
            f"{BASE_URL}/series/observations",
            params={
                "series_id": series_id,
                "api_key": API_KEY,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 6,
            },
            timeout=10,
        ).json()

        observations = obs_resp.get("observations", [])
        if observations:
            lines.append("\n  Recent observations:")
            for obs in observations:
                lines.append(f"    {obs['date']}: {obs['value']}")

        return "\n".join(lines)
    except Exception as e:
        return f"FRED error for {series_id}: {e}"


tool = None
if API_KEY:
    tool = Tool(
        name="fred",
        func=query_fred,
        description=(
            "Fetch macroeconomic data from FRED (Federal Reserve). "
            "Input can be a series ID like 'FEDFUNDS' or keywords like 'CPI', 'GDP', "
            "'unemployment', 'federal funds rate', 'treasury', 'mortgage', 'money supply'. "
            "Best for macro/economic indicators, not individual stocks."
        ),
    )
