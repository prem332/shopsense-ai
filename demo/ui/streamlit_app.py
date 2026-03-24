import sys
import os
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../..")
    )
)

import streamlit as st
from demo.agent.graph import shopping_graph

# Page config
st.set_page_config(
    page_title="ShopSense AI — Demo",
    page_icon="🛍️",
    layout="wide"
)

# Header
st.title("🛍️ ShopSense AI")
st.markdown("*Your personal AI stylist — Demo v0.1*")
st.divider()

# Sidebar filters
with st.sidebar:
    st.header("🎯 Your Preferences")

    category = st.selectbox(
        "Category",
        ["", "shirts", "pants", "shoes", "watches", "accessories"]
    )
    color = st.text_input(
        "Color",
        placeholder="navy blue, red, black..."
    )
    size = st.text_input(
        "Size",
        placeholder="S, M, L, XL or shoe size..."
    )
    occasion = st.selectbox(
        "Occasion",
        ["", "formal", "casual", "wedding", "party", "sports"]
    )
    budget = st.slider(
        "Max Budget (₹)",
        min_value=200,
        max_value=10000,
        value=2000,
        step=100
    )
    brand = st.text_input(
        "Brand (optional)",
        placeholder="Allen Solly, Puma, Titan..."
    )

    st.divider()
    st.caption("💡 Fill filters OR type query below!")

# Main area
st.subheader("💬 Tell me what you're looking for")

user_query = st.text_area(
    "Your query",
    placeholder="e.g. Formal navy shirt size L under ₹1500, prefer Allen Solly",
    height=100
)

search_button = st.button(
    "🔍 Find Products",
    type="primary",
    use_container_width=True
)


def build_query(query, category, color, size, occasion, budget, brand):
    if query.strip():
        return query.strip()
    parts = []
    if brand:
        parts.append(brand)
    if color:
        parts.append(color)
    if category:
        parts.append(category)
    if occasion:
        parts.append(f"for {occasion}")
    if size:
        parts.append(f"size {size}")
    if budget:
        parts.append(f"under ₹{budget}")
    return " ".join(parts) if parts else ""


if search_button:
    final_query = build_query(
        user_query, category, color,
        size, occasion, budget, brand
    )

    if not final_query:
        st.warning("⚠️ Please enter a query or fill filters!")
    else:
        with st.spinner("🤖 Finding best products for you..."):
            try:
                initial_state = {
                    "user_query": final_query,
                    "category": category or None,
                    "color": color or None,
                    "size": size or None,
                    "occasion": occasion or None,
                    "budget_max": float(budget),
                    "brand": brand or None,
                    "products": None,
                    "final_response": None,
                    "error": None
                }

                result = shopping_graph.invoke(initial_state)

                if result.get("error") and not result.get("products"):
                    st.error(f"❌ {result['error']}")

                elif result.get("products"):
                    products = result["products"]
                    st.success(f"✅ Found {len(products)} products!")
                    st.divider()

                    # Preference summary
                    with st.expander(
                        "🧠 Extracted Preferences",
                        expanded=False
                    ):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(
                                "Category",
                                result.get("category") or "N/A"
                            )
                            st.metric(
                                "Color",
                                result.get("color") or "N/A"
                            )
                        with col2:
                            st.metric(
                                "Size",
                                result.get("size") or "N/A"
                            )
                            st.metric(
                                "Occasion",
                                result.get("occasion") or "N/A"
                            )
                        with col3:
                            st.metric(
                                "Budget",
                                f"₹{result.get('budget_max')}"
                                if result.get("budget_max") else "N/A"
                            )
                            st.metric(
                                "Brand",
                                result.get("brand") or "Any"
                            )

                    st.divider()
                    st.subheader("🛍️ Top Recommendations")

                    for i in range(0, len(products), 2):
                        cols = st.columns(2)
                        for j, col in enumerate(cols):
                            if i + j < len(products):
                                p = products[i + j]
                                with col:
                                    with st.container(border=True):
                                        if p.get("image"):
                                            st.image(
                                                p["image"],
                                                use_container_width=True
                                            )
                                        title = p['title']
                                        st.markdown(
                                            f"**{title[:80]}...**"
                                            if len(title) > 80
                                            else f"**{title}**"
                                        )
                                        c1, c2 = st.columns(2)
                                        with c1:
                                            st.markdown(
                                                f"💰 **{p['price']}**"
                                            )
                                        with c2:
                                            st.markdown(
                                                f"⭐ **{p['rating']}**"
                                            )
                                        st.markdown(
                                            f"🏪 **{p['platform']}**"
                                        )
                                        if p.get("link"):
                                            st.link_button(
                                                "🛒 Buy Now",
                                                p["link"],
                                                use_container_width=True
                                            )
                else:
                    st.error("❌ No products found.")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.exception(e)

st.divider()
st.caption(
    "🧪 ShopSense AI v0.1 Demo | "
    "LangGraph + Gemini + Pinecone + SerpAPI"
)
