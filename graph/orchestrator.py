from langgraph.graph import StateGraph, END
from graph.state import FinSightState
from agents.validator import validator_node
from agents.error_handler import error_handler_node
from agents.schemas import StockData, MacroData, NewsData, AnalysisOutput, ReportOutput
from tools.alpha_vantage import fetch_stock_data
from tools.fred_data import fetch_macro_data
from tools.tavily_search import fetch_news
from pydantic import ValidationError
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage


def get_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.3-70b-versatile",
        temperature=0.1
    )


# Real Data Agent
def data_agent(state: FinSightState) -> dict:
    print(f"Data Agent: fetching real stock data for {state['ticker']}")
    try:
        validated = fetch_stock_data(state["ticker"])
        print(f"Data Agent: price ${validated.price}, PE {validated.pe_ratio}")
        return {"stock_data": validated.model_dump()}
    except Exception as e:
        print(f"Data Agent: failed — {e}")
        return {
            "stock_data": {},
            "errors": [f"Data Agent failed: {str(e)}"]
        }


# Real Macro Agent
def macro_agent(state: FinSightState) -> dict:
    print("Macro Agent: fetching real FRED data")
    try:
        validated = fetch_macro_data()
        return {"macro_data": validated.model_dump()}
    except Exception as e:
        print(f"Macro Agent: failed — {e}")
        return {
            "macro_data": {},
            "errors": [f"Macro Agent failed: {str(e)}"]
        }


# Real News Agent
def news_agent(state: FinSightState) -> dict:
    print("News Agent: fetching real news via Tavily")
    try:
        validated = fetch_news(state["ticker"])
        return {"news_data": validated.model_dump()}
    except Exception as e:
        print(f"News Agent: failed — {e}")
        return {
            "news_data": {},
            "errors": [f"News Agent failed: {str(e)}"]
        }


# Real Analysis Agent — uses Groq LLM
def analysis_agent(state: FinSightState) -> dict:
    print("Analysis Agent: running LLM reasoning")
    try:
        llm = get_llm()

        stock = state["stock_data"]
        macro = state["macro_data"]
        news = state["news_data"]

        prompt = f"""
        You are a financial analyst. Analyze this data and provide investment guidance.

        STOCK DATA:
        - Ticker: {stock.get('ticker')}
        - Price: ${stock.get('price')}
        - PE Ratio: {stock.get('pe_ratio', 'N/A')}
        - Market Cap: {stock.get('market_cap', 'N/A')}

        MACRO DATA:
        - Interest Rate: {macro.get('interest_rate')}%
        - Inflation: {macro.get('inflation_rate')}
        - GDP Growth: {macro.get('gdp_growth')}%
        - Unemployment: {macro.get('unemployment_rate')}%

        NEWS SENTIMENT: {news.get('sentiment')}
        RECENT HEADLINES: {', '.join(news.get('headlines', [])[:3])}

        You MUST respond in EXACTLY this format with no extra text:
        SUMMARY: [2-3 sentence analysis]
        RECOMMENDATION: buy
        CONFIDENCE: 0.75
        RISK_LEVEL: medium
        """

        response = llm.invoke([HumanMessage(content=prompt)])
        text = response.content.strip()
        print(f"Analysis Agent raw response:\n{text}")

        # Robust parsing
        summary = ""
        recommendation = "hold"
        confidence = 0.5
        risk_level = "medium"

        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
            elif line.startswith("RECOMMENDATION:"):
                rec = line.replace("RECOMMENDATION:", "").strip().lower()
                if rec in ["buy", "hold", "avoid"]:
                    recommendation = rec
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.replace("CONFIDENCE:", "").strip())
                    confidence = max(0.0, min(1.0, confidence))
                except:
                    confidence = 0.5
            elif line.startswith("RISK_LEVEL:"):
                risk = line.replace("RISK_LEVEL:", "").strip().lower()
                if risk in ["low", "medium", "high"]:
                    risk_level = risk

        validated = AnalysisOutput(
            summary=summary if summary else "Analysis completed",
            recommendation=recommendation,
            confidence=confidence,
            risk_level=risk_level
        )

        print(f"Analysis Agent: {validated.recommendation} with {validated.confidence} confidence")
        return {"analysis": validated.model_dump()}

    except Exception as e:
        print(f"Analysis Agent: failed — {e}")
        return {
            "analysis": {},
            "errors": [f"Analysis Agent failed: {str(e)}"]
        }


# Real Report Agent
def report_agent(state: FinSightState) -> dict:
    print("Report Agent: generating final report")
    try:
        stock = state["stock_data"]
        macro = state["macro_data"]
        news = state["news_data"]
        analysis = state["analysis"]

        report = f"""
        FinSight-AI Investment Brief
        ============================
        Ticker:             {stock.get('ticker')}
        Current Price:      ${stock.get('price')}
        PE Ratio:           {stock.get('pe_ratio', 'N/A')}
        Market Cap:         ${stock.get('market_cap', 'N/A')}

        Macro Context:
        - Interest Rate:    {macro.get('interest_rate')}%
        - Inflation (CPI):  {macro.get('inflation_rate')}
        - GDP Growth:       {macro.get('gdp_growth')}%
        - Unemployment:     {macro.get('unemployment_rate')}%

        News Sentiment:     {news.get('sentiment', 'N/A').upper()}
        Top Headlines:
        {chr(10).join(f"  - {h}" for h in news.get('headlines', [])[:3])}

        Analysis:           {analysis.get('summary')}
        Recommendation:     {analysis.get('recommendation', 'N/A').upper()}
        Confidence:         {float(analysis.get('confidence', 0)) * 100:.0f}%
        Risk Level:         {analysis.get('risk_level', 'N/A').upper()}
        """

        return {"report": report}

    except (ValidationError, KeyError) as e:
        return {
            "report": "Report generation failed",
            "errors": [f"Report Agent failed: {str(e)}"]
        }


# Routing functions
def route_after_validation(state: FinSightState) -> str:
    if state["is_valid"]:
        return "data_agent"
    return "error_handler"


def route_after_data(state: FinSightState) -> str:
    if state["stock_data"]:
        return "macro_agent"
    return "error_handler"


# Build graph
def build_graph():
    graph = StateGraph(FinSightState)

    graph.add_node("validator", validator_node)
    graph.add_node("data_agent", data_agent)
    graph.add_node("macro_agent", macro_agent)
    graph.add_node("news_agent", news_agent)
    graph.add_node("analysis_agent", analysis_agent)
    graph.add_node("report_agent", report_agent)
    graph.add_node("error_handler", error_handler_node)

    graph.set_entry_point("validator")

    graph.add_conditional_edges(
        "validator",
        route_after_validation,
        {
            "data_agent": "data_agent",
            "error_handler": "error_handler"
        }
    )

    graph.add_conditional_edges(
        "data_agent",
        route_after_data,
        {
            "macro_agent": "macro_agent",
            "error_handler": "error_handler"
        }
    )

    graph.add_edge("macro_agent", "news_agent")
    graph.add_edge("news_agent", "analysis_agent")
    graph.add_edge("analysis_agent", "report_agent")
    graph.add_edge("report_agent", END)
    graph.add_edge("error_handler", END)

    return graph.compile()