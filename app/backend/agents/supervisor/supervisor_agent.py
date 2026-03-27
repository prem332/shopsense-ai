import os
from app.backend.a2a.client.supervisor_client import supervisor_client
from app.backend.agents.state import ShopSenseState
from app.backend.memory.conversation_memory import conversation_memory
from dotenv import load_dotenv

load_dotenv()


async def run_supervisor(state: ShopSenseState) -> ShopSenseState:
    """
    Supervisor Agent — A2A CLIENT
    Sprint 2: Basic A2A orchestration
    Sprint 3: Multi-platform + memory + reflection
    Sprint 4: Full alert registration with conditions
    Sprint 5: Gender + budget range support
    """
    print("\n🎯  Supervisor: Starting orchestration...")

    user_query = state.get("user_query", "")
    session_id = state.get("session_id", "default")
    user_id = state.get("user_id", "guest")
    intent = state.get("intent", "recommendation")

    context = conversation_memory.get_context_summary(session_id)

    # ══════════════════════════════════════════════════════════
    # STEP 1: Guardrails
    # ══════════════════════════════════════════════════════════
    print("📡  A2A → GuardrailsAgent: validate_input")
    guardrails_result = await supervisor_client.delegate_task(
        agent_name="GuardrailsAgent",
        skill_id="validate_input",
        payload={"user_query": user_query}
    )

    is_valid = guardrails_result.get("is_valid", True)
    if not is_valid:
        response = "❌ " + guardrails_result.get(
            "rejection_reason", "Invalid query"
        )
        conversation_memory.add_turn(
            session_id, user_query, response, intent
        )
        return {
            **state,
            "is_valid": False,
            "rejection_reason": guardrails_result.get("rejection_reason"),
            "final_response": response
        }

    # ══════════════════════════════════════════════════════════
    # RECOMMENDATION FLOW
    # ══════════════════════════════════════════════════════════
    if intent == "recommendation":

        # Step 2: Extract preferences
        print("📡  A2A → PreferenceAgent: extract_preferences")
        pref_result = await supervisor_client.delegate_task(
            agent_name="PreferenceAgent",
            skill_id="extract_preferences",
            payload={
                "user_query": user_query,
                "user_id": user_id,
                "context": context
            }
        )
        preferences = pref_result.get("preferences", {})

        # ✅ Inject budget_min, budget_max, gender from state
        budget_min = state.get("budget_min") or 0
        budget_max = state.get("budget_max") or 0
        preferences["budget_min"] = budget_min
        preferences["budget_max"] = budget_max

        # ✅ Inject gender
        gender = state.get("gender", "") or ""
        if not gender:
            query_lower = user_query.lower()
            if any(w in query_lower for w in [
                "female", "women", "girl", "ladies", "woman"
            ]):
                gender = "female"
            elif any(w in query_lower for w in [
                "male", "men", "boy", "gents", "man"
            ]):
                gender = "male"

        preferences["gender"] = gender

        print(
            f"   → Budget injected: ₹{budget_min} — ₹{budget_max}"
        )
        print(f"   → Gender injected: {gender}")

        # Step 3: Fetch preference history
        print("📡  A2A → PreferenceAgent: fetch_history")
        history_result = await supervisor_client.delegate_task(
            agent_name="PreferenceAgent",
            skill_id="fetch_history",
            payload={"user_id": user_id}
        )
        history = history_result.get("history", [])
        if history:
            print(f"   → Found {len(history)} past preferences")

        # Step 4: Search with self-reflection loop
        platforms = state.get(
            "platforms",
            ["amazon", "flipkart", "myntra"]
        )
        all_products = []
        reflection_attempts = 0
        max_attempts = 2
        current_query = user_query

        while reflection_attempts < max_attempts:
            print(
                f"📡  A2A → SearchRankAgent: search_products "
                f"(attempt {reflection_attempts + 1})"
            )

            search_result = await supervisor_client.delegate_task(
                agent_name="SearchRankAgent",
                skill_id="search_products",
                payload={
                    "preferences": preferences,
                    "user_query": current_query,
                    "platforms": platforms
                }
            )

            all_products = search_result.get("products", [])

            # Step 5: Self-reflection
            print("📡  A2A → SearchRankAgent: reflect_results")
            reflection_result = await supervisor_client.delegate_task(
                agent_name="SearchRankAgent",
                skill_id="reflect_results",
                payload={
                    "products": all_products,
                    "preferences": preferences,
                    "attempts": reflection_attempts
                }
            )

            if reflection_result.get("passed"):
                print(f"   → ✅ Reflection passed!")
                break

            refined_query = reflection_result.get("refined_query")
            if refined_query:
                print(f"   → 🔄 Refining: {refined_query}")
                current_query = refined_query

            reflection_attempts += 1

        # Step 6: Rank products
        print("📡  A2A → SearchRankAgent: rank_products")
        rank_result = await supervisor_client.delegate_task(
            agent_name="SearchRankAgent",
            skill_id="rank_products",
            payload={
                "products": all_products,
                "preferences": preferences
            }
        )

        ranked = rank_result.get("ranked_products", [])
        print(f"✅  Supervisor: Got {len(ranked)} ranked products")

        response = (
            f"Found {len(ranked)} products "
            f"across {len(platforms)} platforms!"
        )

        conversation_memory.add_turn(
            session_id=session_id,
            user_query=state.get("user_query", ""),
            response=response,
            intent=intent,
            products_count=len(ranked)
        )

        return {
            **state,
            "is_valid": True,
            "category": preferences.get("category"),
            "color": preferences.get("color"),
            "size": preferences.get("size"),
            "skin_tone": preferences.get("skin_tone"),
            "occasion": preferences.get("occasion"),
            "budget_max": preferences.get("budget_max"),
            "brand": preferences.get("brand"),
            "gender": gender,
            "raw_products": all_products,
            "ranked_products": ranked,
            "reflection_passed": True,
            "reflection_attempts": reflection_attempts,
            "final_response": response
        }

    # ══════════════════════════════════════════════════════════
    # ALERT FLOW
    # ══════════════════════════════════════════════════════════
    elif intent == "alert":
        print("📡  A2A → AlertAgent: register_alert")
        alert_result = await supervisor_client.delegate_task(
            agent_name="AlertAgent",
            skill_id="register_alert",
            payload={
                "user_query": user_query,
                "user_id": user_id
            }
        )

        alert_id = alert_result.get("alert_id")
        conditions = alert_result.get("conditions", {})

        condition_parts = []
        if conditions.get("brand"):
            condition_parts.append(f"Brand: {conditions['brand']}")
        if conditions.get("target_price"):
            condition_parts.append(
                f"Price ≤ ₹{conditions['target_price']}"
            )
        if conditions.get("discount_pct"):
            condition_parts.append(
                f"Discount ≥ {conditions['discount_pct']}%"
            )
        if conditions.get("in_stock"):
            condition_parts.append("Back in stock")
        if conditions.get("color"):
            condition_parts.append(f"Color: {conditions['color']}")
        if conditions.get("size"):
            condition_parts.append(f"Size: {conditions['size']}")

        platforms = conditions.get("platforms", [])
        platform_text = " + ".join(
            [p.title() for p in platforms]
        ) if platforms else "All platforms"

        conditions_text = (
            " | ".join(condition_parts)
            if condition_parts
            else "Custom conditions"
        )

        response = (
            f"✅ Alert registered successfully!\n"
            f"🔔 Monitoring: {conditions_text}\n"
            f"🏪 Platforms: {platform_text}\n"
            f"📋 Alert ID: {alert_id}\n"
            f"⏰ Checking every 6 hours"
        )

        conversation_memory.add_turn(
            session_id=session_id,
            user_query=user_query,
            response=response,
            intent=intent
        )

        return {
            **state,
            "is_valid": True,
            "alert_id": alert_id,
            "final_response": response
        }

    return {**state, "final_response": "Request processed!"}