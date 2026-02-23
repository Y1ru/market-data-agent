"""Market Data Trading Agent — entry point.

Initializes a LangChain agent with market data provider tools
and runs an interactive REPL for trading analysis queries.
"""

import logging

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from config import get_llm
from providers import get_tools

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ─── System Prompt ──────────────────────────────────────────────────
# TODO: Implement your agent's system prompt below.
#
# This is the most important design decision for the agent — it shapes
# HOW the agent reasons about market data. Consider:
#
#   - Analysis style: conservative vs. aggressive?
#   - Should it always cross-reference multiple sources?
#   - How should it handle conflicting signals?
#   - Should it include risk warnings / disclaimers?
#   - What's the default analysis framework (technical, fundamental, both)?
#
# Write 5-10 lines that define the agent's personality and approach.
# The prompt has access to {tools} and {tool_names} variables.

SYSTEM_PROMPT = """\
You are a helpful market data assistant. Answer the user's questions using the tools available to you.
"""
# ────────────────────────────────────────────────────────────────────


def build_agent():
    llm = get_llm()
    tools = get_tools()

    if not tools:
        raise RuntimeError("No market data tools available. Check your .env file.")

    logger.info(f"Agent initialized with {len(tools)} tools")

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)


def main():
    print("=" * 60)
    print("  Market Data Trading Agent")
    print("  Type your query or 'quit' to exit")
    print("=" * 60)

    executor = build_agent()
    chat_history = []

    while True:
        try:
            query = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        try:
            result = executor.invoke({"input": query, "chat_history": chat_history})
            output = result.get("output", "No response.")
            print(f"\n{output}")

            # Maintain conversation history
            from langchain_core.messages import HumanMessage, AIMessage
            chat_history.append(HumanMessage(content=query))
            chat_history.append(AIMessage(content=output))
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()
