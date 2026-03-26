import os
import json
import uuid
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


def save_user_preference(
    user_id: str,
    preferences: dict,
    embedding: list
) -> bool:
    """Save user preference with embedding to pgvector"""
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO preferences (
                    id, user_id, category, color, size,
                    skin_tone, occasion, budget_max, brands, embedding
                ) VALUES (
                    :id, :user_id, :category, :color, :size,
                    :skin_tone, :occasion, :budget_max, :brands,
                    :embedding
                )
            """), {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "category": preferences.get("category"),
                "color": [preferences["color"]] if preferences.get("color") else None,
                "size": preferences.get("size"),
                "skin_tone": preferences.get("skin_tone"),
                "occasion": preferences.get("occasion"),
                "budget_max": preferences.get("budget_max"),
                "brands": [preferences["brand"]] if preferences.get("brand") else None,
                "embedding": str(embedding)
            })
            conn.commit()
            print(f"✅ pgvector: Saved preferences for user {user_id}")
            return True

    except Exception as e:
        print(f"⚠️ pgvector save error: {e}")
        return False


def get_similar_preferences(
    user_id: str,
    query_embedding: list,
    limit: int = 3
) -> list:
    """Get similar past preferences using cosine similarity"""
    try:
        with engine.connect() as conn:
            results = conn.execute(text("""
                SELECT
                    category, color, size, occasion,
                    budget_max, brands,
                    1 - (embedding <=> :embedding::vector) AS similarity
                FROM preferences
                WHERE user_id = :user_id
                ORDER BY embedding <=> :embedding::vector
                LIMIT :limit
            """), {
                "user_id": user_id,
                "embedding": str(query_embedding),
                "limit": limit
            })

            history = []
            for row in results:
                history.append({
                    "category": row.category,
                    "color": row.color,
                    "size": row.size,
                    "occasion": row.occasion,
                    "budget_max": float(row.budget_max) if row.budget_max else None,
                    "brands": row.brands,
                    "similarity": float(row.similarity)
                })

            print(f"✅ pgvector: Found {len(history)} past preferences")
            return history

    except Exception as e:
        print(f"⚠️ pgvector search error: {e}")
        return []


def get_user_history(user_id: str, limit: int = 5) -> list:
    """Get recent preferences for a user"""
    try:
        with engine.connect() as conn:
            results = conn.execute(text("""
                SELECT
                    category, color, size, occasion,
                    budget_max, brands, created_at
                FROM preferences
                WHERE user_id = :user_id
                ORDER BY created_at DESC
                LIMIT :limit
            """), {
                "user_id": user_id,
                "limit": limit
            })

            history = []
            for row in results:
                history.append({
                    "category": row.category,
                    "color": row.color,
                    "size": row.size,
                    "occasion": row.occasion,
                    "budget_max": float(row.budget_max) if row.budget_max else None,
                    "brands": row.brands
                })

            return history

    except Exception as e:
        print(f"⚠️ pgvector history error: {e}")
        return []