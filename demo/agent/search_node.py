import os
import hashlib
from demo.agent.state import ShopSenseState
from demo.tools.amazon_tool import search_amazon
from demo.vectorstore.pinecone_store import get_pinecone_index
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)


def search_node(state: ShopSenseState) -> ShopSenseState:
    print("🔍 Search Node: Searching products...")

    # Build search query from preferences
    query_parts = []
    if state.get("brand"):
        query_parts.append(state["brand"])
    if state.get("color"):
        query_parts.append(state["color"])
    if state.get("category"):
        query_parts.append(state["category"])
    if state.get("occasion"):
        query_parts.append(state["occasion"])
    if state.get("size"):
        query_parts.append(f"size {state['size']}")

    search_query = " ".join(
        query_parts
    ) if query_parts else state["user_query"]

    print(f"📝 Query: {search_query}")

    # Search Amazon
    products = search_amazon(
        query=search_query,
        budget_max=state.get("budget_max")
    )

    if not products:
        return {
            **state,
            "products": [],
            "final_response": "No products found. Try different filters.",
            "error": "No products found"
        }

    # Store in Pinecone
    try:
        index = get_pinecone_index()
        vectors = []

        for product in products:
            embedding = embeddings.embed_query(product["title"])
            product_id = hashlib.md5(
                product["title"].encode()
            ).hexdigest()
            vectors.append({
                "id": product_id,
                "values": embedding,
                "metadata": {
                    "title": product["title"],
                    "price": str(product["price"]),
                    "link": product["link"],
                    "platform": product["platform"]
                }
            })

        if vectors:
            index.upsert(vectors=vectors)
            print(f"✅ Stored {len(vectors)} in Pinecone")

    except Exception as e:
        print(f"⚠️ Pinecone error: {e}")

    return {
        **state,
        "products": products,
        "final_response": f"Found {len(products)} products!"
    }