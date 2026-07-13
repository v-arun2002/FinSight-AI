import yfinance as yf
from agents.schemas import StockData

def fetch_stock_data(ticker: str) -> StockData:
    """
    Fetches real-time stock data using yfinance.
    No API key needed, no rate limits.
    """
    print(f"yfinance: fetching data for {ticker}")
    
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # Check if ticker exists
    if not info or "symbol" not in info:
        raise ValueError(f"No data found for ticker {ticker}")
    
    # Extract fields
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    pe_ratio = info.get("trailingPE") or info.get("forwardPE")
    market_cap = info.get("marketCap")
    volume = info.get("volume") or info.get("regularMarketVolume")
    
    if not price:
        raise ValueError(f"Could not get price for {ticker}")
    
    print(f"yfinance: price ${price}, PE {pe_ratio}")
    
    return StockData(
        ticker=ticker,
        price=float(price),
        pe_ratio=float(pe_ratio) if pe_ratio else None,
        market_cap=float(market_cap) if market_cap else None,
        volume=int(volume) if volume else None
    )