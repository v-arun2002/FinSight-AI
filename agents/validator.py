from graph.state import FinSightState

# Known valid ticker format — real validation would call an API
VALID_TICKER_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def validator_node(state: FinSightState) -> dict:
    """
    Validates the ticker before any API calls are made.
    Saves money — no point calling Alpha Vantage on a bad ticker.
    """
    ticker = state["ticker"].strip().upper()
    
    print(f"Validator: checking ticker '{ticker}'")
    
    # Rule 1 — ticker must exist
    if not ticker:
        return {
            "is_valid": False,
            "validation_message": "Ticker is empty",
            "errors": ["Validation failed: ticker is empty"]
        }
    
    # Rule 2 — ticker must be 1-5 uppercase letters only
    if not all(c in VALID_TICKER_CHARS for c in ticker):
        return {
            "is_valid": False,
            "validation_message": f"Invalid ticker format: {ticker}",
            "errors": [f"Validation failed: invalid ticker format '{ticker}'"]
        }
    
    if len(ticker) > 5:
        return {
            "is_valid": False,
            "validation_message": f"Ticker too long: {ticker}",
            "errors": [f"Validation failed: ticker '{ticker}' exceeds 5 characters"]
        }
    
    # Passed all rules
    print(f"Validator: ticker '{ticker}' is valid")
    return {
        "is_valid": True,
        "validation_message": "Valid",
        "ticker": ticker  # normalized to uppercase
    }