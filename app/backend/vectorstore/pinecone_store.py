import os
import hashlib
from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def get_pinecone_index():
    """Get or create Pinecone index for product embeddings"""
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME", "shopsense-products")
    existing = [i.name for i in pc.list_indexes()]

    if index_name not in existing:
        print(f"📦 Creating Pinecone index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        print(f"✅ Index created: {index_name}")
    else:
        print(f"✅ Index exists: {index_name}")

    return pc.Index(index_name)


def store_products(products: list) -> bool:
    """Store product embeddings in Pinecone"""
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
                    "price_num": product.get("price_num") or 0,
                    "link": product["link"],
                    "image": product.get("image", ""),
                    "rating": str(product.get("rating", "N/A")),
                    "platform": product["platform"]
                }
            })

        if vectors:
            index.upsert(vectors=vectors)
            print(f"✅ Stored {len(vectors)} products in Pinecone")

        return True

    except Exception as e:
        print(f"⚠️ Pinecone storage error: {e}")
        return False


def search_similar_products(query: str, top_k: int = 5) -> list:
    """Search similar products using vector similarity"""
    try:
        index = get_pinecone_index()
        query_embedding = embeddings.embed_query(query)

        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        products = []
        for match in results.matches:
            if match.metadata:
                products.append({
                    "title": match.metadata.get("title"),
                    "price": match.metadata.get("price"),
                    "price_num": match.metadata.get("price_num"),
                    "link": match.metadata.get("link"),
                    "image": match.metadata.get("image"),
                    "rating": match.metadata.get("rating"),
                    "platform": match.metadata.get("platform"),
                    "similarity_score": match.score
                })

        print(f"✅ Found {len(products)} similar products in Pinecone")
        return products

    except Exception as e:
        print(f"⚠️ Pinecone search error: {e}")
        return []