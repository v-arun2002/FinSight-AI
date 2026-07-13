import os
from tavily import TavilyClient
from agents.schemas import NewsData

def fetch_news(ticker: str, company_name: str = "") -> NewsData:
    """
    Searches for latest news about a stock using Tavily.
    Returns a validated NewsData Pydantic model.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    client = TavilyClient(api_key=api_key)
    
    # Build search query
    query = f"{ticker} {company_name} stock news analysis 2025".strip()
    print(f"Tavily: searching for '{query}'")
    
    response = client.search(
        query=query,
        search_depth="basic",
        max_results=5,
        include_answer=True
    )
    
    # Extract headlines from results
    headlines = []
    for result in response.get("results", []):
        title = result.get("title", "")
        if title:
            headlines.append(title)
    
    # Simple sentiment from Tavily's answer summary
    answer = response.get("answer", "").lower()
    
    if any(word in answer for word in ["surge", "gain", "beat", "growth", "strong", "positive"]):
        sentiment = "positive"
    elif any(word in answer for word in ["fall", "drop", "miss", "weak", "concern", "negative"]):
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    print(f"Tavily: found {len(headlines)} headlines, sentiment {sentiment}")
    
    return NewsData(
        headlines=headlines,
        sentiment=sentiment,
        source_count=len(headlines)
    )