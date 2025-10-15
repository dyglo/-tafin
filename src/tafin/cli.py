from dotenv import load_dotenv

# Load environment variables BEFORE importing any tafin modules
load_dotenv()

from tafin.agent import Agent
from tafin.model import LLMUnavailableError, OPENAI_API_KEY
from tafin.tools import run_alpha_vantage, run_web_search
from tafin.utils.intro import print_intro
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

SEARCH_HELP = (
    "Search mode commands:\n"
    "  ?help                Show this message\n"
    "  alpha <symbol> [fn]  Call Alpha Vantage (fn defaults to TIME_SERIES_DAILY)\n"
    "  <anything else>      Runs a Serper web search\n"
    "  exit / quit          Leave TAFIN\n"
)


def run_search_mode(reason: str = ""):
    """Fallback mode when no OpenAI key is configured or authentication fails."""
    if reason:
        print(reason)
    else:
        print("OpenAI API key not detected. Entering search-only mode.")
    print(SEARCH_HELP)
    session = PromptSession(history=InMemoryHistory())

    while True:
        try:
            raw = session.prompt("tafin-search> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not raw:
            continue
        lowered = raw.lower()
        if lowered in {"exit", "quit"}:
            print("Goodbye!")
            break
        if lowered in {"?help", "help"}:
            print(SEARCH_HELP)
            continue

        if lowered.startswith("alpha "):
            parts = raw.split()
            if len(parts) < 2:
                print("Usage: alpha <symbol> [function]")
                continue
            symbol = parts[1].upper()
            function = parts[2] if len(parts) > 2 else "TIME_SERIES_DAILY"
            try:
                data = run_alpha_vantage(function=function, symbol=symbol)
            except Exception as exc:
                print(f"Alpha Vantage error: {exc}")
                continue
            print(f"\nAlpha Vantage ({function}) for {symbol}:")
            for key, value in list(data.items())[:5]:
                print(f"- {key}: {value if isinstance(value, (str, int, float)) else '...'}")
            print()
            continue

        try:
            result = run_web_search(query=raw)
        except Exception as exc:
            print(f"Search error: {exc}")
            continue

        print(f"\nTop results for: {raw}")
        results = result.get("results", [])
        if not results:
            print("No results found.\n")
            continue
        for idx, item in enumerate(results, start=1):
            title = item.get("title") or "Untitled result"
            link = item.get("link") or "No link provided"
            snippet = item.get("snippet") or ""
            print(f"{idx}. {title}\n   {link}\n   {snippet}\n")


def main():
    print_intro()
    if not OPENAI_API_KEY:
        run_search_mode()
        return

    agent = Agent()
    session = PromptSession(history=InMemoryHistory())

    while True:
        try:
            query = session.prompt("tafin> ")
            if query.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            if query:
                agent.run(query)
        except LLMUnavailableError as exc:
            run_search_mode(str(exc))
            break
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
