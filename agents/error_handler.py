from graph.state import FinSightState

def error_handler_node(state: FinSightState) -> dict:
    """
    Catches failures from any agent and builds a clean error report.
    Pipeline never crashes — it always returns something meaningful.
    """
    print(f"Error Handler: pipeline failed with {len(state['errors'])} error(s)")
    
    error_summary = "\n".join(state["errors"])
    
    report = f"""
    FinSight-AI Pipeline Error Report
    ==================================
    Query: {state['query']}
    Ticker: {state['ticker']}
    
    Errors encountered:
    {error_summary}
    
    Please check your ticker symbol and try again.
    """
    
    return {"report": report}