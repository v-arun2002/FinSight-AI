from typing import TypedDict, Annotated, Optional
import operator
from agents.schemas import StockData, MacroData, NewsData, AnalysisOutput

class FinSightState(TypedDict):
    # User input
    query: str          
    ticker: str         
    
    # Validation
    is_valid: bool
    validation_message: str
    
    # Agent outputs — now typed with Pydantic models
    stock_data: Optional[dict]          # will hold StockData.model_dump()
    macro_data: Optional[dict]          # will hold MacroData.model_dump()
    news_data: Optional[dict]           # will hold NewsData.model_dump()
    analysis: Optional[dict]            # will hold AnalysisOutput.model_dump()
    report: str         
    
    # Error tracking
    errors: Annotated[list, operator.add]