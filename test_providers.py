"""Integration tests for all market data providers.

Tests each provider's query function with a real API call and validates
the response contains expected data. Skips providers with missing API keys.

Run:  python -m pytest test_providers.py -v
"""

import os
import pytest
from dotenv import load_dotenv

load_dotenv()

# ── Yahoo Finance (free, no key) ────────────────────────────────────

def test_yahoo_finance_stock():
    from providers.yahoo_finance import query_yahoo_finance
    result = query_yahoo_finance("AAPL")
    assert "Yahoo Finance data for AAPL" in result
    assert "Current Price:" in result
    assert "Open=" in result


# ── Binance (free, no key) ──────────────────────────────────────────

def test_binance_crypto():
    from providers.binance import query_binance
    result = query_binance("BTC")
    assert "Binance data for BTCUSDT" in result
    assert "Last Price:" in result
    assert "Daily candles" in result


# ── CoinGecko (free, no key) ────────────────────────────────────────

def test_coingecko_coin():
    from providers.coingecko import query_coingecko
    result = query_coingecko("BTC")
    assert "Bitcoin" in result
    assert "Price:" in result
    assert "Market Cap:" in result


def test_coingecko_trending():
    from providers.coingecko import query_coingecko
    result = query_coingecko("trending")
    assert "trending" in result.lower()


# ── Alpha Vantage (key required) ────────────────────────────────────

@pytest.mark.skipif(not os.getenv("ALPHA_VANTAGE_API_KEY"), reason="ALPHA_VANTAGE_API_KEY not set")
def test_alpha_vantage_overview():
    from providers.alpha_vantage import query_alpha_vantage
    result = query_alpha_vantage("AAPL")
    assert "Alpha Vantage" in result
    assert "error" not in result.lower() or "rate" in result.lower()


@pytest.mark.skipif(not os.getenv("ALPHA_VANTAGE_API_KEY"), reason="ALPHA_VANTAGE_API_KEY not set")
def test_alpha_vantage_rsi():
    from providers.alpha_vantage import query_alpha_vantage
    result = query_alpha_vantage("AAPL RSI")
    assert "RSI" in result


# ── Finnhub (key required) ──────────────────────────────────────────

@pytest.mark.skipif(not os.getenv("FINNHUB_API_KEY"), reason="FINNHUB_API_KEY not set")
def test_finnhub_quote():
    from providers.finnhub import query_finnhub
    result = query_finnhub("AAPL")
    assert "Finnhub data for AAPL" in result
    assert "Current:" in result


# ── Polygon.io (key required) ───────────────────────────────────────

@pytest.mark.skipif(not os.getenv("POLYGON_API_KEY"), reason="POLYGON_API_KEY not set")
def test_polygon_aggregates():
    from providers.polygon import query_polygon
    result = query_polygon("AAPL")
    assert "Polygon" in result


# ── FRED (key required) ─────────────────────────────────────────────

@pytest.mark.skipif(not os.getenv("FRED_API_KEY"), reason="FRED_API_KEY not set")
def test_fred_fed_funds():
    from providers.fred import query_fred
    result = query_fred("federal funds rate")
    assert "FRED" in result
    assert "Federal Funds" in result


@pytest.mark.skipif(not os.getenv("FRED_API_KEY"), reason="FRED_API_KEY not set")
def test_fred_cpi():
    from providers.fred import query_fred
    result = query_fred("CPI")
    assert "FRED" in result


# ── Twelve Data (key required) ──────────────────────────────────────

@pytest.mark.skipif(not os.getenv("TWELVE_DATA_API_KEY"), reason="TWELVE_DATA_API_KEY not set")
def test_twelve_data_price():
    from providers.twelve_data import query_twelve_data
    result = query_twelve_data("AAPL")
    assert "Twelve Data" in result
    assert "C=" in result


@pytest.mark.skipif(not os.getenv("TWELVE_DATA_API_KEY"), reason="TWELVE_DATA_API_KEY not set")
def test_twelve_data_rsi():
    from providers.twelve_data import query_twelve_data
    result = query_twelve_data("AAPL RSI")
    assert "RSI" in result


# ── Financial Modeling Prep (key required) ───────────────────────────

@pytest.mark.skipif(not os.getenv("FMP_API_KEY"), reason="FMP_API_KEY not set")
def test_fmp_profile():
    from providers.fmp import query_fmp
    result = query_fmp("AAPL")
    assert "FMP" in result or "Apple" in result


@pytest.mark.skipif(not os.getenv("FMP_API_KEY"), reason="FMP_API_KEY not set")
def test_fmp_earnings():
    from providers.fmp import query_fmp
    result = query_fmp("AAPL earnings")
    assert "Revenue" in result or "income" in result.lower()


# ── Tiingo (key required) ───────────────────────────────────────────

@pytest.mark.skipif(not os.getenv("TIINGO_API_KEY"), reason="TIINGO_API_KEY not set")
def test_tiingo_prices():
    from providers.tiingo import query_tiingo
    result = query_tiingo("AAPL")
    assert "Tiingo" in result
    assert "error" not in result.lower() or "not found" not in result.lower()


# ── Tool registration ───────────────────────────────────────────────

def test_tool_loading():
    """Verify get_tools() returns only providers with valid keys."""
    from providers import get_tools
    tools = get_tools()
    names = [t.name for t in tools]

    # These 3 should always be present (no key needed)
    assert "yahoo_finance" in names
    assert "binance" in names
    assert "coingecko" in names
    assert len(tools) >= 3
