import os
from fredapi import Fred
from agents.schemas import MacroData

# FRED series IDs — these are official Federal Reserve data codes
SERIES = {
    "interest_rate": "FEDFUNDS",      # Federal Funds Rate
    "inflation_rate": "CPIAUCSL",     # Consumer Price Index
    "gdp_growth": "A191RL1Q225SBEA",  # Real GDP Growth Rate
    "unemployment_rate": "UNRATE"     # Unemployment Rate
}

def fetch_macro_data() -> MacroData:
    """
    Fetches latest macroeconomic indicators from FRED.
    Returns a validated MacroData Pydantic model.
    """
    api_key = os.getenv("FRED_API_KEY")
    fred = Fred(api_key=api_key)
    
    print("FRED: fetching macroeconomic indicators")
    
    results = {}
    
    for field, series_id in SERIES.items():
        try:
            # Get last 1 observation — most recent value
            series = fred.get_series(series_id)
            latest_value = float(series.dropna().iloc[-1])
            results[field] = latest_value
            print(f"FRED: {field} = {latest_value}")
        except Exception as e:
            print(f"FRED: could not fetch {field} — {e}")
            results[field] = None
    
    return MacroData(**results)