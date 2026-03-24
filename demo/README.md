# 🧪 ShopSense AI — v0.1 Demo

Standalone prototype to validate core concept.

## What This Demo Does
- Extracts preferences from natural language using Gemini
- Searches Amazon via SerpAPI
- Stores product embeddings in Pinecone
- Returns top 5 recommendations with image, price, link

## Architecture
User Input → Preference Node → Search Node → Streamlit UI
## Tech Stack
- LLM: Gemini 1.5 Flash
- Agent: LangGraph (2 nodes)
- Vector DB: Pinecone
- Search: SerpAPI (Amazon)
- UI: Streamlit

## How to Run
```bash
cd demo
source venv/bin/activate
streamlit run ui/streamlit_app.py
