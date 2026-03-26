import os
import json
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from demo.agent.state import ShopSenseState
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1
)


def preference_node(state: ShopSenseState) -> ShopSenseState:
    print("🧠 Preference Node: Extracting preferences...")

    system_prompt = """You are a shopping assistant that extracts
    structured preferences from user queries.

    Extract these fields:
    - category: product type (shirts, shoes, watches, pants etc.)
    - color: preferred color
    - size: clothing or shoe size
    - occasion: formal, casual, wedding, party, sports etc.
    - budget_max: maximum budget in INR (number only)
    - brand: preferred brand name

    Return ONLY a valid JSON object. No explanation. No markdown.
    If a field is not mentioned, set it to null.

    Example:
    {
        "category": "shirts",
        "color": "navy blue",
        "size": "L",
        "occasion": "formal",
        "budget_max": 1500,
        "brand": "Allen Solly"
    }"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["user_query"])
    ]

    response = llm.invoke(messages)

    try:
        raw = response.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        preferences = json.loads(raw)
        print(f"✅ Preferences: {preferences}")

        return {
            **state,
            "category": preferences.get("category"),
            "color": preferences.get("color"),
            "size": preferences.get("size"),
            "occasion": preferences.get("occasion"),
            "budget_max": preferences.get("budget_max"),
            "brand": preferences.get("brand"),
        }

    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return {
            **state,
            "error": f"Could not extract preferences: {str(e)}"
        }
