# FinSight

### AI-powered investment research. Any stock. Under 30 seconds.

**[finsight-ai-imjw.onrender.com](https://finsight-ai-imjw.onrender.com)** · [API Docs](https://finsight-ai-imjw.onrender.com/docs) · [LinkedIn](https://www.linkedin.com/in/arun-valliappan-990334263/)

---

## What it does

Type a ticker. Ask a question. Get a full investment brief.

FinSight pulls live stock fundamentals, Federal Reserve macroeconomic data, and real-time news — then runs LLM reasoning across all three sources to return a structured recommendation with confidence score and risk assessment.
NVDA → "Is this a good buy given AI tailwinds?"
→ Recommendation:  BUY
→ Confidence:      75%
→ Risk level:      MEDIUM
→ Price:           $204.21  |  P/E: 32.26  |  Market cap: $5.11T
→ Fed funds rate:  3.63%    |  GDP growth: 2.1%
→ News sentiment:  POSITIVE
→ Analysis:        NVIDIA's dominant AI infrastructure position
justifies premium valuation despite macro headwinds...

---

## Why it's interesting

Most RAG and LLM demos work on static documents. FinSight runs on **live data** — every request pulls fresh prices, the latest Fed figures, and breaking news. The brief you get at 9am is different from the one at 4pm.

The pipeline is also production-grade, not a notebook:

- **Conditional routing** — if market data fails, the pipeline routes to an error handler and returns a clean response rather than crashing
- **Typed data contracts** — every component output is validated against a Pydantic schema before passing downstream, so bad data fails loudly at the source
- **Containerized and deployed** — Docker image, CI/CD via GitHub → Render, auto-deploys on every push
- **Real API** — not a Streamlit demo, a proper FastAPI service with documented endpoints

---

## Pipeline
POST /research
↓
┌─────────────────────────────────────────────────────────┐
│                    LangGraph Orchestrator                │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Market Data │  │ Macro Data  │  │  News Scan  │     │
│  │  yfinance   │  │    FRED     │  │   Tavily    │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         └────────────────┼────────────────┘             │
│                          ↓                              │
│                  Pydantic AI validation                  │
│                          ↓                              │
│              Analysis + Brief (Groq LLM)                │
└─────────────────────────────────────────────────────────┘
↓
JSON response

---

## Stack

| | |
|---|---|
| Orchestration | LangGraph |
| Data contracts | Pydantic AI |
| API | FastAPI |
| LLM | Groq — Llama 3.3 70B |
| Market data | yfinance |
| Macro data | FRED (Federal Reserve) |
| News | Tavily |
| Container | Docker |
| Deployment | Render |
| CI/CD | GitHub → Render (auto-deploy on push) |

---

## API

**POST** `https://finsight-ai-imjw.onrender.com/research`

```bash
curl -X POST https://finsight-ai-imjw.onrender.com/research \
  -H "Content-Type: application/json" \
  -d '{"ticker": "NVDA", "query": "Is this a good long-term investment?"}'
```

```json
{
  "ticker": "NVDA",
  "recommendation": "buy",
  "confidence": 0.75,
  "risk_level": "medium",
  "stock_data": { "price": 204.21, "pe_ratio": 32.26, "market_cap": 5109662089216 },
  "macro_data": { "interest_rate": 3.63, "gdp_growth": 2.1, "unemployment_rate": 4.2 },
  "news_data": { "sentiment": "positive", "headlines": ["..."] },
  "report": "...",
  "errors": []
}
```

Full docs at [finsight-ai-imjw.onrender.com/docs](https://finsight-ai-imjw.onrender.com/docs)

---

## Run locally

```bash
git clone https://github.com/v-arun2002/FinSight-AI
cd FinSight-AI
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

```env
# .env
GROQ_API_KEY=your_key
FRED_API_KEY=your_key
TAVILY_API_KEY=your_key
```

```bash
uvicorn api.main:app --reload --port 8000
```

## Run with Docker

```bash
docker build -t finsight-ai .
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e FRED_API_KEY=your_key \
  -e TAVILY_API_KEY=your_key \
  finsight-ai
```

---

## Structure
finsight-ai/
├── agents/
│   ├── schemas.py          # Pydantic AI typed contracts per component
│   ├── validator.py        # Input validation with conditional routing
│   └── error_handler.py    # Graceful failure handling
├── graph/
│   ├── state.py            # Shared LangGraph state definition
│   └── orchestrator.py     # Pipeline, routing logic, and error recovery
├── tools/
│   ├── alpha_vantage.py    # yfinance integration
│   ├── fred_data.py        # FRED API integration
│   └── tavily_search.py    # Tavily news search
├── api/
│   └── main.py             # FastAPI app, endpoints, response models
├── frontend.html           # Production UI served at /
├── Dockerfile
└── requirements.txt

---

## One thing to know

The free Render tier spins down after inactivity. First request after a period of no traffic takes 30–60 seconds to cold start. Subsequent requests are fast.

---

> FinSight is for informational purposes only and does not constitute financial advice. Always consult a qualified financial advisor before making investment decisions.

---

Built by [Arun Valliappan](https://www.linkedin.com/in/arun-valliappan-990334263/)
