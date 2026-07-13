from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from graph.orchestrator import build_graph

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="FinSight-AI",
    description="Multi-agent financial research system powered by LangGraph",
    version="1.0.0"
)

# Build graph once at startup — not on every request
graph = build_graph()

# ---- Request/Response Models ----

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

# ---- Endpoints ----

@app.get("/health")
def health_check():
    """
    Health check endpoint.
    Render and Docker ping this to verify app is running.
    """
    return {"status": "ok", "service": "FinSight-AI"}

@app.post("/research", response_model=ResearchResponse)
async def run_research(request: ResearchRequest):
    """
    Main endpoint — runs full multi-agent pipeline.
    Accepts ticker and query, returns investment brief.
    """
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
        
        # Extract analysis fields safely
        analysis = result.get("analysis") or {}
        
        return ResearchResponse(
            ticker=result.get("ticker", request.ticker),
            recommendation=analysis.get("recommendation", "unavailable"),
            confidence=float(analysis.get("confidence", 0.0)),
            risk_level=analysis.get("risk_level", "unavailable"),
            report=result.get("report", ""),
            errors=result.get("errors", [])
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline failed: {str(e)}"
        )