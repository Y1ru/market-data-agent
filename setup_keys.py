"""Interactive helper to register for free API keys and write them to .env.

Opens each provider's signup page in your browser, then prompts you to
paste the key. Writes all keys to .env when done.
"""

import webbrowser
import shutil
from pathlib import Path

ENV_FILE = Path(__file__).parent / ".env"
ENV_EXAMPLE = Path(__file__).parent / ".env.example"

PROVIDERS = [
    {
        "name": "Alpha Vantage",
        "env_var": "ALPHA_VANTAGE_API_KEY",
        "url": "https://www.alphavantage.co/support/#api-key",
        "note": "Fill the form and click 'Get Free API Key'. Key appears instantly.",
    },
    {
        "name": "Finnhub",
        "env_var": "FINNHUB_API_KEY",
        "url": "https://finnhub.io/register",
        "note": "Sign up, then find your API key on the dashboard.",
    },
    {
        "name": "Polygon.io",
        "env_var": "POLYGON_API_KEY",
        "url": "https://polygon.io/dashboard/signup",
        "note": "Sign up for a free account. Key is on the dashboard under 'Keys'.",
    },
    {
        "name": "FRED (Federal Reserve)",
        "env_var": "FRED_API_KEY",
        "url": "https://fred.stlouisfed.org/docs/api/api_key.html",
        "note": "Click 'Request or view your API keys'. Requires a free FRED account.",
    },
    {
        "name": "Twelve Data",
        "env_var": "TWELVE_DATA_API_KEY",
        "url": "https://twelvedata.com/register",
        "note": "Sign up, then find your key under Account > API Keys.",
    },
    {
        "name": "Financial Modeling Prep",
        "env_var": "FMP_API_KEY",
        "url": "https://site.financialmodelingprep.com/register",
        "note": "Sign up for free tier. Key is on the dashboard.",
    },
    {
        "name": "Tiingo",
        "env_var": "TIINGO_API_KEY",
        "url": "https://www.tiingo.com/account/api/token",
        "note": "Sign up, then go to API > Token to see your key.",
    },
]


def load_existing_env():
    """Load existing .env values into a dict."""
    values = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                values[key.strip()] = val.strip()
    return values


def write_env(values):
    """Write values back to .env, preserving the template structure."""
    if not ENV_FILE.exists():
        shutil.copy(ENV_EXAMPLE, ENV_FILE)

    lines = ENV_FILE.read_text().splitlines()
    output = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in values and values[key]:
                output.append(f"{key}={values[key]}")
                continue
        output.append(line)
    ENV_FILE.write_text("\n".join(output) + "\n")


def main():
    print("=" * 60)
    print("  API Key Setup Helper")
    print("  Opens signup pages & saves keys to .env")
    print("=" * 60)

    existing = load_existing_env()

    # Check which keys are already set
    needed = []
    for p in PROVIDERS:
        val = existing.get(p["env_var"], "")
        if val:
            print(f"\n  [already set] {p['name']}")
        else:
            needed.append(p)

    if not needed:
        print("\nAll 7 API keys are already set in .env!")
        return

    print(f"\n{len(needed)} keys to set up. Press Enter to open each signup page.")
    print("Paste the key when you have it, or press Enter to skip.\n")

    for p in needed:
        print("-" * 60)
        print(f"  {p['name']}")
        print(f"  {p['note']}")
        print(f"  URL: {p['url']}")
        print("-" * 60)

        try:
            input("Press Enter to open signup page...")
        except (EOFError, KeyboardInterrupt):
            print("\nSkipping remaining providers.")
            break

        webbrowser.open(p["url"])

        try:
            key = input(f"Paste your {p['name']} API key (or Enter to skip): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSkipping remaining providers.")
            break

        if key:
            existing[p["env_var"]] = key
            print(f"  Saved {p['env_var']}")
        else:
            print("  Skipped.")

    # Ensure .env exists before writing
    if not ENV_FILE.exists():
        shutil.copy(ENV_EXAMPLE, ENV_FILE)

    write_env(existing)

    # Summary
    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)
    final = load_existing_env()
    for p in PROVIDERS:
        val = final.get(p["env_var"], "")
        status = "set" if val else "missing"
        print(f"  {p['name']:30s} [{status}]")
    print(f"\nKeys saved to {ENV_FILE}")


if __name__ == "__main__":
    main()
