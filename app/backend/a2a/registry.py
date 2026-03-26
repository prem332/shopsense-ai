import json
from pathlib import Path

CARDS_DIR = Path(__file__).parent / "agent_cards"


class AgentRegistry:
    """
    Central registry of all A2A agents.
    Supervisor uses this to discover agents dynamically.
    """

    def __init__(self):
        self.agents = {}
        self._load_all_cards()

    def _load_all_cards(self):
        for card_file in CARDS_DIR.glob("*.json"):
            with open(card_file) as f:
                card = json.load(f)
                self.agents[card["name"]] = card
        print(f"✅  A2A Registry: {len(self.agents)} agents loaded")
        for name in self.agents:
            print(f"    → {name}")

    def get_agent(self, name: str) -> dict:
        return self.agents.get(name)

    def get_all_agents(self) -> dict:
        return self.agents

    def get_agent_endpoint(self, name: str) -> str:
        agent = self.get_agent(name)
        return agent["endpoint"] if agent else None

    def get_agent_skills(self, name: str) -> list:
        agent = self.get_agent(name)
        return agent.get("skills", []) if agent else []

    def find_agent_by_skill(self, skill_id: str) -> dict:
        for agent in self.agents.values():
            for skill in agent.get("skills", []):
                if skill["id"] == skill_id:
                    return agent
        return None


# Global registry instance
registry = AgentRegistry()