# ShopSense AI 🛍️
### Your Personal AI Shopping Stylist

[![CI](https://github.com/prem332/shopsense-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/prem332/shopsense-ai/actions/workflows/ci.yml)
[![CD](https://github.com/prem332/shopsense-ai/actions/workflows/cd.yml/badge.svg)](https://github.com/prem332/shopsense-ai/actions/workflows/cd.yml)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 🔗 Live Demo

| Service | URL |
|---------|-----|
| **Frontend** | https://shopsense-ai-one.vercel.app |
| **Backend API** | https://shopsense-ai-backend-ansjznbbxq-el.a.run.app |
| **API Health** | https://shopsense-ai-backend-ansjznbbxq-el.a.run.app/health |

---

## 🤔 Problem — Why ShopSense AI?

### Limitations of Existing E-Commerce Platforms

| Problem | Amazon / Flipkart / Myntra |
|---------|---------------------------|
| **Search** | Keyword-based only — no understanding of context |
| **Personalization** | No memory of past preferences |
| **Multi-platform** | Shop one platform at a time |
| **Budget** | Manual price filters only |
| **Safety** | No guardrails for harmful queries |
| **Intelligence** | No AI reasoning or reflection |

### Our Solution — ShopSense AI

| Feature | ShopSense AI |
|---------|-------------|
| **Search** | Natural language — "I am a male, blue shirt size M between 1500 and 3000" |
| **Personalization** | Remembers preferences via pgvector (Supabase) |
| **Multi-platform** | Searches Amazon via SerpAPI |
| **Budget** | Extracts budget from natural language automatically |
| **Safety** | PII detection, harmful intent blocking, prompt injection protection |
| **Intelligence** | Multi-agent reflection loop — re-searches if results are poor |

---

## 🏗️ Architecture

```
+------------------------------------------------------------------+
|                        USER (Browser)                            |
|              https://shopsense-ai-one.vercel.app                 |
+------------------------------------------------------------------+
                              |
                              | HTTPS
                              |
+------------------------------------------------------------------+
|                  Next.js Frontend (Vercel)                       |
|      ChatPanel | FilterPanel | ProductCard | AlertsTab           |
+------------------------------------------------------------------+
                              |
                              | REST API
                              |
+------------------------------------------------------------------+
|             FastAPI Backend (GCP Cloud Run) :8000                |
|                                                                  |
|  +------------------------------------------------------------+  |
|  |                   LangGraph Pipeline                       |  |
|  |   Guardrails --> Intent --> Supervisor --> Response        |  |
|  +------------------------------------------------------------+  |
|                              |                                   |
|                 Google A2A Protocol                              |
|                              |                                   |
|  +-----------+-----------+-----------+-----------+              |
|  |   :8001   |   :8002   |   :8003   |   :8004   |             |
|  |           |           |           |           |              |
|  | Guardrails| Preference|  Search   |   Alert   |             |
|  |   Agent   |   Agent   |   Rank    |   Agent   |             |
|  |           |           |   Agent   |           |              |
|  +-----------+-----------+-----------+-----------+              |
+------------------------------------------------------------------+
                              |
             +----------------+----------------+
             |                |                |
    +--------+------+  +------+-------+  +----+----------+
    |               |  |              |  |               |
    |    SerpAPI    |  |   Pinecone   |  |   Supabase    |
    |  Amazon.in    |  |  Vector DB   |  |  PostgreSQL   |
    |    Search     |  |   Products   |  |  Preferences  |
    |               |  |              |  |   + Alerts    |
    +---------------+  +--------------+  +---------------+
```

---

## 🤖 5 A2A Agents

| Agent | Port | Responsibility |
|-------|------|----------------|
| **GuardrailsAgent** | 8001 | PII detection, harmful intent, prompt injection blocking |
| **PreferenceAgent** | 8002 | Extract preferences from natural language using Gemini |
| **SearchRankAgent** | 8003 | Search Amazon via SerpAPI, rank products by score |
| **AlertAgent** | 8004 | Register and manage price/stock alerts |
| **Supervisor** | — | Orchestrates all agents via Google A2A Protocol |

---

## 🛡️ Guardrails — 3 Layers of Protection

### Layer 1 — PII Detection
Detects and blocks:
- Aadhaar number (12-digit pattern)
- PAN card (ABCDE1234F format)
- Phone numbers (10-digit Indian)
- Email addresses
- Credit/debit card numbers
- Bank account numbers
- IFSC codes, Passport, Voter ID

### Layer 2 — Harmful Intent
Blocks queries related to:
- Weapons, explosives, firearms
- Drugs and narcotics
- Hate speech and terrorism
- Illegal activities and fraud

### Layer 3 — Prompt Injection
Blocks attempts like:
- "Ignore previous instructions"
- "Act as a different AI"
- "Jailbreak", "Override", "Bypass"
- System prompt manipulation

---

## 📊 RAGAS Evaluation Results

| Metric | Score |
|--------|-------|
| **Faithfulness** | 0.8778 |
| **Answer Relevancy** | 0.7357 |
| **Context Precision** | 1.0000 |
| **Context Recall** | 0.7500 |
| **Average Score** | 0.8409 |

```
Model      : gemini-2.5-flash (Google)
Embeddings : all-MiniLM-L6-v2 (HuggingFace)
Test Cases : 3 e-commerce queries
```

---

## 🧪 Unit Tests

```
39 tests | 0 failures | 100% pass rate

TestPIIDetection        (7 tests)  PASS
TestHarmfulIntent       (7 tests)  PASS
TestPromptInjection     (6 tests)  PASS
TestShoppingValidation  (6 tests)  PASS
TestBudgetExtraction    (7 tests)  PASS
TestSmartSelect         (6 tests)  PASS
```

Run tests:
```bash
pytest tests/test_guardrails.py tests/test_budget.py -v
```

---

## 🚀 Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| FastAPI | REST API framework |
| LangGraph | Multi-agent graph orchestration |
| Google A2A Protocol | Agent-to-agent communication |
| Gemini 2.5 Flash | LLM for preference extraction |
| SerpAPI | Amazon product search |
| Pinecone | Vector store for product embeddings |
| pgvector (Supabase) | User preference history |
| LangSmith | Observability and tracing |

### Frontend
| Technology | Purpose |
|-----------|---------|
| Next.js 14 | React framework |
| TypeScript | Type safety |
| Tailwind CSS | Styling |
| Vercel | Hosting |

### DevOps
| Technology | Purpose |
|-----------|---------|
| Docker | Containerization |
| GCP Cloud Run | Serverless backend hosting |
| GitHub Actions | CI/CD pipeline |
| Artifact Registry | Docker image storage |

---

## ⚙️ CI/CD Pipeline

```
git push origin main
        |
        v
+---------------------------------------+
|         CI Pipeline (ci.yml)          |
|  - Install dependencies               |
|  - Check Python imports               |
|  - Run 39 unit tests                  |
|  - Build Docker image                 |
+---------------------------------------+
        |
        | Only if CI passes
        v
+---------------------------------------+
|         CD Pipeline (cd.yml)          |
|  - Authenticate to GCP               |
|  - Build Docker image                 |
|  - Push to Artifact Registry          |
|  - Deploy to Cloud Run                |
|  - Health check on live URL           |
+---------------------------------------+
        |
        v
+---------------------------------------+
|      Frontend (Vercel)                |
|  - Auto-deploys on every push         |
|  - No manual steps needed             |
+---------------------------------------+
```

---

## 🏃 Running Locally

### Prerequisites
```
Python 3.11+
Node.js 18+
```

### Backend Setup
```bash
# Clone repo
git clone https://github.com/prem332/shopsense-ai.git
cd shopsense-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp app/backend/.env.example app/backend/.env
# Add your API keys

# Start all servers
bash start_servers.sh
```

### Frontend Setup
```bash
cd app/frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

### Access
```
Frontend : http://localhost:3000
Backend  : http://localhost:8000
API Docs : http://localhost:8000/docs
```

---

## 🔐 Environment Variables

```env
# LLM
GEMINI_API_KEY=your_gemini_key

# Search
SERPAPI_KEY=your_serpapi_key

# Vector DB
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=shopsense-products

# Database
DATABASE_URL=your_supabase_postgresql_url
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Observability
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=shopsense-ai
```

---

## 📁 Project Structure

```
shopsense-ai/
+-- app/
|   +-- backend/
|   |   +-- main.py                     # FastAPI app
|   |   +-- agents/
|   |   |   +-- graph.py               # LangGraph pipeline
|   |   |   +-- state.py               # ShopSenseState
|   |   |   +-- supervisor/            # Supervisor agent
|   |   |   +-- alerts/               # Alert agents
|   |   +-- a2a/
|   |   |   +-- registry.py            # Agent registry
|   |   |   +-- client/               # A2A client
|   |   |   +-- servers/              # 4 A2A servers
|   |   |   +-- agent_cards/          # Agent capability cards
|   |   +-- tools/
|   |   |   +-- amazon_tool.py        # SerpAPI Amazon search
|   |   +-- vectorstore/
|   |   |   +-- pinecone_store.py     # Product embeddings
|   |   |   +-- pgvector_store.py     # Preference history
|   |   +-- memory/
|   |   |   +-- conversation_memory.py
|   |   +-- scheduler/
|   |   |   +-- price_monitor.py      # Background price checker
|   |   +-- evaluation/
|   |       +-- ragas_eval.py         # RAGAS evaluation script
|   |       +-- results.json          # Evaluation results
|   +-- frontend/
|       +-- app/
|       |   +-- page.tsx              # Main page
|       |   +-- layout.tsx
|       +-- components/
|           +-- ChatPanel.tsx         # Chat interface
|           +-- FilterPanel.tsx       # Filter sidebar
|           +-- ProductCard.tsx       # Product display
|           +-- AlertsTab.tsx         # Alerts management
+-- tests/
|   +-- test_guardrails.py            # 26 guardrail tests
|   +-- test_budget.py                # 13 budget tests
+-- demo/                             # v0.1 Streamlit demo
+-- .github/workflows/
|   +-- ci.yml                        # CI pipeline
|   +-- cd.yml                        # CD pipeline
+-- Dockerfile
+-- start_servers.sh                  # Local dev startup
+-- start_servers_prod.sh             # Production startup
+-- requirements.txt
```

---

## 🎯 Key Features

### 1. Natural Language Shopping
```
Input  : "I am a male, blue cotton shirt size L between 1500 and 3000"
Extract: gender=male, color=blue, size=L, budget=1500-3000
Search : Amazon with extracted filters
Output : Top 10 ranked products
```

### 2. Smart Budget Detection
```
Chat message : "between 1500 and 6000" --> overrides filter panel
Filter panel : 0-2000                  --> used only if no chat budget
```

### 3. Self-Reflection Loop
```
Attempt 1 --> 0 products found
           --> Reflection: "Too few results"
           --> Refine query automatically
Attempt 2 --> Products found
```

### 4. Price and Stock Alerts
```
Input   : "Alert me when Allen Solly shirt drops below 999"
Register: Alert saved in Supabase
Monitor : Price check every 6 hours
Notify  : When condition is met
```

---

## 👨‍💻 Author

**Prem Kumar Kale**
- B.Tech, IIIT Sri City
- AI/ML Engineer

---