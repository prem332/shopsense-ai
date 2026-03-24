from langgraph.graph import StateGraph, END
from demo.agent.state import ShopSenseState
from demo.agent.preference_node import preference_node
from demo.agent.search_node import search_node

def create_graph():
    print("🔧 Building ShopSense Demo Graph...")

    graph = StateGraph(ShopSenseState)

    graph.add_node("preference_node", preference_node)
    graph.add_node("search_node", search_node)

    graph.set_entry_point("preference_node")

    graph.add_edge("preference_node", "search_node")
    graph.add_edge("search_node", END)

    app = graph.compile()
    print("✅ Demo Graph ready!")
    return app


# Global graph instance
shopping_graph = create_graph()
