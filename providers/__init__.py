"""Collect all available provider tools.

Tools requiring API keys are only included if the key is set in the environment.
"""

import logging

from providers.yahoo_finance import tool as yahoo_finance_tool
from providers.alpha_vantage import tool as alpha_vantage_tool
from providers.finnhub import tool as finnhub_tool
from providers.polygon import tool as polygon_tool
from providers.fred import tool as fred_tool
from providers.binance import tool as binance_tool
from providers.twelve_data import tool as twelve_data_tool
from providers.fmp import tool as fmp_tool
from providers.tiingo import tool as tiingo_tool
from providers.coingecko import tool as coingecko_tool

logger = logging.getLogger(__name__)

_ALL = [
    ("Yahoo Finance", yahoo_finance_tool),
    ("Alpha Vantage", alpha_vantage_tool),
    ("Finnhub", finnhub_tool),
    ("Polygon.io", polygon_tool),
    ("FRED", fred_tool),
    ("Binance", binance_tool),
    ("Twelve Data", twelve_data_tool),
    ("Financial Modeling Prep", fmp_tool),
    ("Tiingo", tiingo_tool),
    ("CoinGecko", coingecko_tool),
]


def get_tools():
    """Return list of available tools, skipping any with missing API keys."""
    tools = []
    for name, tool in _ALL:
        if tool is not None:
            tools.append(tool)
            logger.info(f"Loaded provider: {name}")
        else:
            logger.warning(f"Skipped provider: {name} (API key not set)")
    return tools
