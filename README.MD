# FinSight — AI Investment Research

![Python](https://img.shields.io/badge/Python-3.12-blue) ![LangGraph](https://img.shields.io/badge/LangGraph-1.2.9-green) ![FastAPI](https://img.shields.io/badge/FastAPI-0.139-teal) ![Docker](https://img.shields.io/badge/Docker-28.3-blue) ![Pydantic AI](https://img.shields.io/badge/Pydantic_AI-2.9-purple)

**Live at: [finsight-ai-imjw.onrender.com](https://finsight-ai-imjw.onrender.com)** · [API Docs](https://finsight-ai-imjw.onrender.com/docs)

A deployed multi-agent financial research system that combines live market data, Federal Reserve macroeconomic indicators, and real-time news to generate structured investment briefs — served via a production FastAPI backend with Docker containerization and CI/CD auto-deploy.

---

## What makes this different

Most LLM portfolio projects call a single API and display the response. FinSight is architected as a production system.

**Multi-source data fusion** — a single investment question pulls from three independent live data sources simultaneously: yfinance for stock fundamentals, the Federal Reserve FRED API for macroeconomic indicators, and Tavily for real-time news. The LLM reasons across all three in a single analysis pass. Most demos use static documents.

**LangGraph orchestration with conditional routing** — the pipeline is not a linear chain. Each node writes to shared state and the graph makes routing decisions at runtime. If market data fails, a conditional edge routes to an error handler that returns a clean structured response. If the ticker is invalid, the validator node short-circuits the entire pipeline before any external API is called — saving latency and cost.

**Pydantic AI typed contracts** — every node output is validated against a strict Pydantic model before being written to state. A malformed API response fails loudly at the source with a descriptive error, not silently three nodes later with a cryptic KeyError. Field-level validators enforce domain logic: price must be positive, recommendation must be one of buy/hold/avoid, confidence must be between 0.0 and 1.0.

**Real deployment, not a demo** — the system runs in a Docker container on Render with CI/CD auto-deploy on every push to main. The API is publicly accessible and documented at `/docs`. This is not a Streamlit app running on localhost.

---

## Sample output

```
Ticker:  NVDA
Query:   Is this a good buy given current macro conditions?

Recommendation:  BUY
Confidence:      75%
Risk level:      MEDIUM

Stock fundamentals:
  Price:       $204.21
  P/E ratio:   32.26
  Market cap:  $5.11T
  Volume:      45,000,000

Macro context (FRED):
  Fed funds rate:  3.63%
  CPI index:       333.9
  GDP growth:      2.1%
  Unemployment:    4.2%

News sentiment:  POSITIVE
Headlines:
  01  NVIDIA Soars 39% in 2025: Will the Stock Carry Momentum in 2026?
  02  NVIDIA Stock Forecast 2025: Impact of AI Innovations
  03  Nvidia Stock Has 70% Potential Upside For 2025

Analysis:
  NVIDIA's dominant position in AI infrastructure justifies its premium
  valuation despite elevated interest rates. Positive news momentum and
  strong GDP growth support a bullish near-term outlook, though the high
  P/E ratio introduces valuation risk if sentiment shifts.
```

---

## Architecture

```
POST /research
       |
       v
FastAPI — Pydantic request validation
       |
       v
LangGraph StateGraph (FinSightState)
       |
       v
+---------------------------+
|      Validator Node       |
|  checks ticker format     |
|  invalid? --> Error Node  |
+---------------------------+
       |
       | valid
       v
+---------------+   +---------------+   +---------------+
|   Data Node   |   |   Macro Node  |   |   News Node   |
|   yfinance    |   |   FRED API    |   |   Tavily      |
|   StockData   |   |   MacroData   |   |   NewsData    |
|  (Pydantic)   |   |  (Pydantic)   |   |  (Pydantic)   |
+---------------+   +---------------+   +---------------+
       |                   |                   |
       +-------------------+-------------------+
                           |
              empty stock_data? --> Error Node
                           |
                           | has data
                           v
+--------------------------------------------------+
|               Analysis Node                      |
|   Groq Llama 3.3 70B                            |
|   reasons across stock + macro + news            |
|   returns: summary, recommendation,              |
|   confidence, risk_level                         |
|   validated by AnalysisOutput (Pydantic)         |
+--------------------------------------------------+
                           |
                           v
+--------------------------------------------------+
|               Report Node                        |
|   formats final investment brief from state      |
+--------------------------------------------------+
                           |
                           v
              FastAPI JSON response
                           |
                           v
              Frontend (served at /)
```

---

## Tech stack

| Layer | Tool | Why |
|---|---|---|
| Agent orchestration | LangGraph 1.2.9 | Explicit state management, conditional routing, production-standard for agentic workflows |
| Data contracts | Pydantic AI 2.9 | Field-level validation at every node boundary, typed state throughout |
| API | FastAPI 0.139 | Async, auto-generated OpenAPI docs, native Pydantic integration |
| LLM | Groq — Llama 3.3 70B | Fast inference on a capable open model, cost-effective for portfolio use |
| Market data | yfinance | Unlimited requests, no API key, reliable for portfolio-scale usage |
| Macro data | FRED (Federal Reserve) | Authoritative government source for interest rates, CPI, GDP, unemployment |
| News | Tavily | Purpose-built for LLM pipelines, returns clean structured results with summaries |
| Container | Docker | Identical environment across local and Render, reproducible builds |
| Deployment | Render | Cloud deployment from Docker image, free tier sufficient for demo |
| CI/CD | GitHub to Render webhook | Auto-deploy on every push to main |

---

## Key engineering decisions

**Why LangGraph over a simple function chain**

A function chain has no state management and no conditional routing. In LangGraph, all nodes share a typed state object — every field written by one node is immediately available to all subsequent nodes without passing arguments. Conditional edges allow runtime routing decisions: an invalid ticker never reaches the FRED or Tavily APIs, and a data failure routes to a structured error response instead of an unhandled exception. This is the difference between a script and a system.

**Why Pydantic AI for data contracts**

Without typed contracts between nodes, a bad API response propagates silently through the pipeline. yfinance occasionally returns None for pe_ratio on certain tickers — without validation, this silently becomes "None" in the final brief. With Pydantic AI, every node validates its output before writing to state. The field validators enforce domain logic: price must be positive, confidence must be between 0.0 and 1.0, sentiment must be one of positive/negative/neutral. Failures are caught at the source.

**Why yfinance over Alpha Vantage**

Alpha Vantage's free tier allows 25 requests/day — insufficient for active development. During a single debugging session you can exhaust the daily limit. yfinance is unlimited, requires no API key, and returns identical data. The resume signal difference between the two is negligible compared to the development productivity loss of a 25-call daily ceiling.

**Why FRED for macro data**

FRED is maintained by the St. Louis Federal Reserve and is the authoritative source for US macroeconomic indicators. The data is free, well-documented, has a stable Python client, and covers 800,000+ series. Using FRED instead of scraped data or a paid provider signals that you understand where institutional financial data actually comes from.

**Why Docker over direct deployment**

Direct deployment without Docker works — until your local Python version does not match the server, or a dependency resolves differently across environments, or a Windows-specific package breaks on the Linux server. Docker eliminates all of this by shipping a reproducible environment. The same image that runs locally on Windows runs identically on Render's Linux servers.

**Why FastAPI over Streamlit**

Streamlit cannot be called programmatically, has no API contract, and produces demos that only work through a browser. FastAPI exposes a documented REST API that any client can call — browser, curl, another service, a mobile app. The /docs endpoint provides interactive documentation at zero cost. For a system that is supposed to demonstrate production thinking, serving it through Streamlit would undercut the entire architecture.

---

## Data sources

| Source | What it provides | Update frequency |
|---|---|---|
| yfinance | Current price, P/E ratio, market cap, trading volume | Real-time (15min delay) |
| FRED — FEDFUNDS | Federal funds rate | Monthly |
| FRED — CPIAUCSL | Consumer Price Index | Monthly |
| FRED — A191RL1Q225SBEA | Real GDP growth rate | Quarterly |
| FRED — UNRATE | Unemployment rate | Monthly |
| Tavily | News headlines and sentiment from live web | Real-time |

---

## Limitations

Being honest about limitations is part of good engineering.

**No historical data** — FinSight pulls the latest available value for each FRED series. It does not show trends over time. A rising interest rate environment looks identical to a falling one at a single snapshot.

**CPI displayed as index value** — FRED's CPIAUCSL series returns an index value (currently ~334) not a percentage rate. This is correct — CPI is an index, not a percentage change — but it reads unexpectedly to users who expect a percentage. Year-over-year percentage change would require two FRED calls and is not currently implemented.

**LLM output format sensitivity** — the analysis node uses a structured prompt and line-by-line parsing to extract recommendation, confidence, and risk level from the Groq response. If the LLM deviates significantly from the expected format, parsing falls back to safe defaults (hold, 0.5, medium) rather than failing. This is intentional defensive behavior but means edge cases may return conservative defaults.

**Render free tier cold starts** — the service spins down after 15 minutes of inactivity. The first request after inactivity takes 30–60 seconds while the container restarts. Subsequent requests are fast.

**No streaming** — the pipeline runs synchronously. The user waits for all five nodes to complete before seeing any output. Streaming partial results via FastAPI's StreamingResponse would improve perceived performance but is not implemented.

**Ticker tape is static** — the scrolling ticker tape on the frontend displays hardcoded prices. It does not reflect real-time market data.

---

## Project structure

```
finsight-ai/
├── agents/
│   ├── schemas.py           # Pydantic AI models: StockData, MacroData, NewsData, AnalysisOutput, ReportOutput
│   ├── validator.py         # Ticker validation node with format checks and normalization
│   └── error_handler.py     # Error handler node — builds structured error report from accumulated errors
├── graph/
│   ├── state.py             # FinSightState TypedDict — shared pipeline state definition
│   └── orchestrator.py      # LangGraph StateGraph — all nodes, edges, and conditional routing
├── tools/
│   ├── alpha_vantage.py     # yfinance market data integration
│   ├── fred_data.py         # FRED API — 4 macroeconomic series with per-field error handling
│   └── tavily_search.py     # Tavily news search with keyword-based sentiment inference
├── api/
│   └── main.py              # FastAPI app — endpoints, response models, frontend file serving
├── frontend.html            # Production UI served at /
├── Dockerfile               # python:3.12-slim, installs deps, runs uvicorn on 0.0.0.0:8000
├── requirements.txt         # Minimal direct dependencies, no platform-specific pins
└── README.md
```

---

## Run locally

```bash
git clone https://github.com/v-arun2002/FinSight-AI
cd FinSight-AI
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `.env` in the root:

```
GROQ_API_KEY=your_key_here
FRED_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

```bash
uvicorn api.main:app --reload --port 8000
```

Open [localhost:8000](http://localhost:8000)

---

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

## API

Full interactive docs at [finsight-ai-imjw.onrender.com/docs](https://finsight-ai-imjw.onrender.com/docs)

**POST /research**

```bash
curl -X POST https://finsight-ai-imjw.onrender.com/research \
  -H "Content-Type: application/json" \
  -d '{"ticker": "NVDA", "query": "Is this a good long-term buy?"}'
```

```json
{
  "ticker": "NVDA",
  "recommendation": "buy",
  "confidence": 0.75,
  "risk_level": "medium",
  "stock_data": {
    "price": 204.21,
    "pe_ratio": 32.26,
    "market_cap": 5109662089216,
    "volume": 45000000
  },
  "macro_data": {
    "interest_rate": 3.63,
    "inflation_rate": 333.9,
    "gdp_growth": 2.1,
    "unemployment_rate": 4.2
  },
  "news_data": {
    "sentiment": "positive",
    "headlines": ["NVIDIA Soars 39% in 2025..."],
    "source_count": 5
  },
  "report": "FinSight Investment Brief...",
  "errors": []
}
```

**GET /health**

```json
{"status": "ok", "service": "FinSight-AI"}
```

---

> FinSight is for informational purposes only and does not constitute financial advice. Always consult a qualified financial advisor before making investment decisions.

---

Built by [Arun Valliappan](https://www.linkedin.com/in/arun-valliappan-990334263/) — MS Data Analytics Engineering, Northeastern University
