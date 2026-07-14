from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from graph.orchestrator import build_graph

load_dotenv()

app = FastAPI(
    title="FinSight-AI",
    description="Multi-agent financial research system powered by LangGraph",
    version="1.0.1"
)

graph = build_graph()

class ResearchRequest(BaseModel):
    query: str
    ticker: str

class ResearchResponse(BaseModel):
    ticker: str
    recommendation: str
    confidence: float
    risk_level: str
    report: str
    errors: list
    stock_data: dict = {}
    macro_data: dict = {}
    news_data: dict = {}
    analysis: dict = {}

@app.get("/")
def root():
    return FileResponse("frontend.html")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "FinSight-AI"}

@app.post("/research", response_model=ResearchResponse)
async def run_research(request: ResearchRequest):
    initial_state = {
        "query": request.query,
        "ticker": request.ticker,
        "is_valid": False,
        "validation_message": "",
        "stock_data": {},
        "macro_data": {},
        "news_data": {},
        "analysis": {},
        "report": "",
        "errors": []
    }
    try:
        result = graph.invoke(initial_state)
        analysis = result.get("analysis") or {}
        return ResearchResponse(
            ticker=result.get("ticker", request.ticker),
            recommendation=analysis.get("recommendation", "unavailable"),
            confidence=float(analysis.get("confidence", 0.0)),
            risk_level=analysis.get("risk_level", "unavailable"),
            report=result.get("report", ""),
            errors=result.get("errors", []),
            stock_data=result.get("stock_data", {}),
            macro_data=result.get("macro_data", {}),
            news_data=result.get("news_data", {}),
            analysis=analysis
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")