import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()


def get_pinecone_index():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME", "shopsense-demo")
    existing = [i.name for i in pc.list_indexes()]

    if index_name not in existing:
        print(f"📦 Creating index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        print(f"✅ Index created!")
    else:
        print(f"✅ Index exists: {index_name}")

    return pc.Index(index_name)