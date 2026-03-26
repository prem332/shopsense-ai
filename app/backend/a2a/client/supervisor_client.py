import httpx
from app.backend.a2a.registry import registry


class SupervisorClient:
    """
    Supervisor Agent acts as A2A CLIENT.
    Discovers agents via registry.
    Delegates tasks via HTTP JSON-RPC.
    """

    def __init__(self):
        self.registry = registry
        print("✅  Supervisor A2A Client initialized")

    async def delegate_task(
        self,
        agent_name: str,
        skill_id: str,
        payload: dict
    ) -> dict:
        endpoint = self.registry.get_agent_endpoint(agent_name)
        if not endpoint:
            return {"error": f"Agent {agent_name} not found"}

        # A2A JSON-RPC 2.0 format
        message = {
            "jsonrpc": "2.0",
            "id": f"{agent_name}:{skill_id}",
            "method": "message/send",
            "params": {
                "skill_id": skill_id,
                "payload": payload
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                print(f"📡  A2A → '{skill_id}' to {agent_name}")
                response = await client.post(
                    f"{endpoint}/a2a",
                    json=message,
                    headers={"Content-Type": "application/json"}
                )
                result = response.json()
                print(f"✅  A2A ← Response from {agent_name}")
                return result.get("result", {})

        except Exception as e:
            print(f"❌  A2A Error: {agent_name}: {e}")
            return {"error": str(e)}

    def discover_agents(self) -> dict:
        return self.registry.get_all_agents()

    def find_agent_for_skill(self, skill_id: str) -> dict:
        return self.registry.find_agent_by_skill(skill_id)


# Global client instance
supervisor_client = SupervisorClient()