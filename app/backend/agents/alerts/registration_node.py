import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine, text
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.1
)


def extract_alert_details(user_query: str) -> dict:
    """
    Use LLM to extract alert conditions from natural language.
    """
    system_prompt = """Extract alert conditions from user query.
    Return ONLY valid JSON. No markdown. No explanation.

    Fields to extract:
    - product_name: product description
    - brand: brand name (null if not mentioned)
    - color: color (null if not mentioned)
    - size: size (null if not mentioned)
    - platform: list of platforms ["amazon","flipkart","myntra"]
    - target_price: price threshold in INR (null if not mentioned)
    - discount_pct: minimum discount % (null if not mentioned)
    - in_stock: true if user wants stock alert (false default)
    - new_arrival: true if user wants new arrival alert (false default)

    Example:
    {
        "product_name": "Allen Solly shirt",
        "brand": "Allen Solly",
        "color": null,
        "size": null,
        "platform": ["amazon", "flipkart", "myntra"],
        "target_price": 999,
        "discount_pct": null,
        "in_stock": false,
        "new_arrival": false
    }"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_query)
        ])

        raw = response.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)

    except Exception as e:
        print(f"⚠️ Alert extraction failed: {e}")
        return {
            "product_name": user_query,
            "brand": None,
            "color": None,
            "size": None,
            "platform": ["amazon", "flipkart", "myntra"],
            "target_price": None,
            "discount_pct": None,
            "in_stock": False,
            "new_arrival": False
        }


def register_alert_in_db(
    user_id: str,
    alert_details: dict
) -> str:
    """Save alert to Supabase PostgreSQL"""
    alert_id = str(uuid.uuid4())

    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO alerts (
                    id, user_id, product_name, brand,
                    color, size, platform, target_price,
                    discount_pct, in_stock, new_arrival,
                    is_active, created_at
                ) VALUES (
                    :id, :user_id, :product_name, :brand,
                    :color, :size, :platform, :target_price,
                    :discount_pct, :in_stock, :new_arrival,
                    true, :created_at
                )
            """), {
                "id": alert_id,
                "user_id": str(user_id),
                "product_name": alert_details.get("product_name"),
                "brand": alert_details.get("brand"),
                "color": alert_details.get("color"),
                "size": alert_details.get("size"),
                "platform": alert_details.get(
                    "platform",
                    ["amazon", "flipkart", "myntra"]
                ),
                "target_price": alert_details.get("target_price"),
                "discount_pct": alert_details.get("discount_pct"),
                "in_stock": alert_details.get("in_stock", False),
                "new_arrival": alert_details.get("new_arrival", False),
                "created_at": datetime.now()
            })
            conn.commit()

        print(f"✅ Alert saved to Supabase: {alert_id}")
        return alert_id

    except Exception as e:
        print(f"❌ Alert DB save failed: {e}")
        return alert_id


def registration_node(
    user_id: str,
    user_query: str
) -> dict:
    """
    Registration Node:
    1. Extract alert conditions from natural language
    2. Save to Supabase
    3. Return alert details
    """
    print("📝 Registration Node: Extracting alert conditions...")

    # Extract conditions using LLM
    alert_details = extract_alert_details(user_query)
    print(f"   → Extracted: {alert_details}")

    # Save to database
    alert_id = register_alert_in_db(str(user_id), alert_details)

    return {
        "alert_id": alert_id,
        "alert_details": alert_details,
        "status": "registered"
    }