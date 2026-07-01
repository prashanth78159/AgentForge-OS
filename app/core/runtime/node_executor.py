
from app.services.llm_service import LLMService
from app.core.tools.tool_registry import ToolRegistry
# Removed: from google.colab import userdata # For secure API key handling

class NodeExecutor:

    def __init__(self, llm_provider: str, api_key: str, model_name: str):
        # 🔑 Initialize LLMService with provider, API key, and model name
        self.llm = LLMService(llm_provider, api_key, model_name)
        self.tool_registry = ToolRegistry()
        # Register tools in the __init__ method
        self.tool_registry.register("print", lambda p: f"Printed {p.get('message', '')}")

    async def execute(self, node, context):
        if node.type == "llm":
            return await self._execute_llm(node, context)

        if node.type == "tool":
            return self._execute_tool(node, context)

        return None

    async def _execute_llm(self, node, context):
        prompt = node.config.get("prompt", "")
        # LLMService.generate now returns (content, prompt_tokens, completion_tokens, cost)
        response_content, prompt_tokens, completion_tokens, total_cost = self.llm.generate(prompt)
        # For now, just return the content, but the metrics are available for future use
        return {
            "output": response_content,
            "metrics": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_cost": total_cost
            }
        }

    def _execute_tool(self, node, context):
        # Extract 'action' as the tool name, as defined in your workflow Node config
        tool_name = node.config.get("action")
        params = node.config.get("params", {})
        if not tool_name:
            raise ValueError("Tool node config must specify an 'action'.")
        return {"output": self.tool_registry.execute(tool_name, params)}
