# Market Data Trading Agent

A LangChain-powered AI agent that connects to 10 market data providers as tools, allowing cross-referencing of live data for trading analysis.

## Providers

| Provider | Key Required | What It Returns |
|----------|:---:|---|
| Yahoo Finance | No | Price history, fundamentals, 52-week range |
| Binance | No | Crypto spot prices, 24h stats, daily candles |
| CoinGecko | No | Crypto prices, market cap, trending coins |
| Alpha Vantage | Yes (free) | Technical indicators (RSI, SMA, EMA, MACD, BBANDS) |
| Finnhub | Yes (free) | Real-time quotes, company news headlines |
| FRED | Yes (free) | Macro data — fed funds rate, CPI, GDP, unemployment |
| Twelve Data | Yes (free) | Real-time/historical prices, 800+ technical indicators |
| Financial Modeling Prep | Yes (free) | Company profile, earnings, financial statements |
| Tiingo | Yes (free) | Historical EOD prices, stock metadata |
| Polygon.io | Yes (free) | Daily aggregates, ticker details |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

Fill in your API keys in `.env`. At minimum you need `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` for the LLM. The 3 free providers (Yahoo, Binance, CoinGecko) work immediately with no keys.

To quickly sign up for the remaining free-tier keys:

```bash
python setup_keys.py
```

## Usage

```bash
python main.py
```

Example queries:

```
> What's AAPL's price trend this week?
> Get the RSI for TSLA
> What's the current federal funds rate?
> Is Bitcoin overbought? Check multiple sources
> Compare AAPL fundamentals across providers
```

The agent automatically selects which providers to query based on your question and cross-references data when relevant.

## Testing

Verify all your provider connections:

```bash
python -m pytest test_providers.py -v
```

Providers with missing API keys are automatically skipped.

## Project Structure

```
├── main.py               # Agent REPL — initialize and run queries
├── config.py             # LLM provider selection (OpenAI / Anthropic)
├── providers/
│   ├── __init__.py       # Collects all available tools
│   ├── yahoo_finance.py  # Yahoo Finance (free)
│   ├── alpha_vantage.py  # Alpha Vantage — technicals
│   ├── finnhub.py        # Finnhub — quotes + news
│   ├── polygon.py        # Polygon.io — aggregates
│   ├── fred.py           # FRED — macro/economic data
│   ├── binance.py        # Binance — crypto spot
│   ├── twelve_data.py    # Twelve Data — technicals
│   ├── fmp.py            # Financial Modeling Prep — fundamentals
│   ├── tiingo.py         # Tiingo — historical prices
│   └── coingecko.py      # CoinGecko — crypto overview
├── test_providers.py     # Integration tests for all providers
├── setup_keys.py         # Interactive API key setup helper
├── requirements.txt
├── .env.example          # Template with all API key fields
└── .gitignore
```
