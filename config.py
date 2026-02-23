import os
from dotenv import load_dotenv

load_dotenv()

# Estimated cost per query (assuming ~2K tokens input + ~500 tokens output per tool call,
# and a typical query uses 2-3 tool calls).
LLM_INFO = {
    "openai":    {"model": "gpt-4o",                    "cost": "~$0.01-0.03/query"},
    "anthropic": {"model": "claude-sonnet-4-5-20250929", "cost": "~$0.01-0.04/query"},
    "groq":      {"model": "llama-3.3-70b-versatile",   "cost": "Free (30 req/min limit)"},
    "ollama":    {"model": "llama3.1",                   "cost": "Free (runs locally)"},
}


def get_llm():
    """Create an LLM instance based on LLM_PROVIDER env var.

    Priority: explicit LLM_PROVIDER > first available key.
    Free options: 'ollama' (local) or 'groq' (cloud, free tier).
    """
    provider = os.getenv("LLM_PROVIDER", "").lower()
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    # Explicit provider selection
    if provider == "ollama":
        from langchain_ollama import ChatOllama
        model = os.getenv("OLLAMA_MODEL", "llama3.1")
        print(f"Using Ollama ({model}) — free, local")
        return ChatOllama(model=model, temperature=0)

    if provider == "groq" and groq_key:
        from langchain_groq import ChatGroq
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        print(f"Using Groq ({model}) — free tier")
        return ChatGroq(model=model, temperature=0)

    if provider == "anthropic" and anthropic_key:
        from langchain_anthropic import ChatAnthropic
        print("Using Anthropic (claude-sonnet-4-5) — ~$0.01-0.04/query")
        return ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0)

    if provider == "openai" and openai_key:
        from langchain_openai import ChatOpenAI
        print("Using OpenAI (gpt-4o) — ~$0.01-0.03/query")
        return ChatOpenAI(model="gpt-4o", temperature=0)

    # Auto-detect: try free options first, then paid
    if groq_key:
        from langchain_groq import ChatGroq
        print("Using Groq (auto-detected) — free tier")
        return ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

    if openai_key:
        from langchain_openai import ChatOpenAI
        print("Using OpenAI (auto-detected) — ~$0.01-0.03/query")
        return ChatOpenAI(model="gpt-4o", temperature=0)

    if anthropic_key:
        from langchain_anthropic import ChatAnthropic
        print("Using Anthropic (auto-detected) — ~$0.01-0.04/query")
        return ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0)

    raise RuntimeError(
        "No LLM configured. Options:\n"
        "  Free:  Set LLM_PROVIDER=ollama (local) or GROQ_API_KEY (cloud)\n"
        "  Paid:  Set OPENAI_API_KEY or ANTHROPIC_API_KEY\n"
        "  See .env.example for details."
    )
