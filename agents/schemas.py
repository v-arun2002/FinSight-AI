from pydantic import BaseModel, Field, field_validator
from typing import Optional

class StockData(BaseModel):
    """Contract for Data Agent output"""
    ticker: str
    price: float
    pe_ratio: Optional[float] = None    # some stocks don't have PE ratio
    market_cap: Optional[float] = None
    volume: Optional[int] = None
    
    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError(f"Price must be positive, got {v}")
        return v
    
    @field_validator("ticker")
    @classmethod
    def ticker_must_be_uppercase(cls, v):
        return v.upper()


class MacroData(BaseModel):
    """Contract for Macro Agent output"""
    interest_rate: Optional[float] = None
    inflation_rate: Optional[float] = None
    gdp_growth: Optional[float] = None
    unemployment_rate: Optional[float] = None
    
@field_validator("interest_rate", "inflation_rate")
@classmethod
def rate_must_be_reasonable(cls, v):
    if v is not None and not (-5.0 <= v <= 500.0):
        raise ValueError(f"Rate {v} is outside reasonable bounds")
    return v


class NewsData(BaseModel):
    """Contract for News Agent output"""
    headlines: list[str]
    sentiment: str = "neutral"          # positive, negative, neutral
    source_count: int = 0
    
    @field_validator("sentiment")
    @classmethod
    def sentiment_must_be_valid(cls, v):
        allowed = {"positive", "negative", "neutral"}
        if v not in allowed:
            raise ValueError(f"Sentiment must be one of {allowed}")
        return v


class AnalysisOutput(BaseModel):
    """Contract for Analysis Agent output"""
    summary: str
    recommendation: str                 # buy, hold, avoid
    confidence: float                   # 0.0 to 1.0
    risk_level: str                     # low, medium, high
    
    @field_validator("recommendation")
    @classmethod
    def recommendation_must_be_valid(cls, v):
        allowed = {"buy", "hold", "avoid"}
        if v.lower() not in allowed:
            raise ValueError(f"Recommendation must be one of {allowed}")
        return v.lower()
    
    @field_validator("confidence")
    @classmethod
    def confidence_must_be_valid(cls, v):
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"Confidence must be between 0 and 1, got {v}")
        return v


class ReportOutput(BaseModel):
    """Contract for Report Agent output"""
    ticker: str
    query: str
    recommendation: str
    summary: str
    risk_level: str
    confidence_score: float
    full_report: str