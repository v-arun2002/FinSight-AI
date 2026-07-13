from dotenv import load_dotenv
from graph.orchestrator import build_graph

load_dotenv()

def run(query: str, ticker: str):
    graph = build_graph()
    
    initial_state = {
        "query": query,
        "ticker": ticker,
        "is_valid": False,
        "validation_message": "",
        "stock_data": {},
        "macro_data": {},
        "news_data": [],
        "analysis": "",
        "report": "",
        "errors": []
    }
    
    result = graph.invoke(initial_state)
    
    print("\n--- Final Report ---")
    print(result["report"])
    print("\n--- Errors ---")
    print(result["errors"] if result["errors"] else "None")

if __name__ == "__main__":
    print("=" * 50)
    print("TEST 1: Valid ticker")
    print("=" * 50)
    run("Is NVIDIA a good investment?", "NVDA")
    
    print("\n" + "=" * 50)
    print("TEST 2: Invalid ticker")
    print("=" * 50)
    run("Tell me about this company", "INVALID123!!")