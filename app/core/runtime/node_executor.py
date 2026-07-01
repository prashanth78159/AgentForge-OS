
from app.services.llm_service import LLMService
from app.core.tools.tool_registry import ToolRegistry
from google.colab import userdata # For secure API key handling

class NodeExecutor:

    def __init__(self):
        # 🔑 Get your API key securely from Colab secrets
        groq_api_key = userdata.get('GROQ_API_KEY') # Assuming you've set 'GROQ_API_KEY' in Colab secrets
        self.llm = LLMService(api_key=groq_api_key)
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
        return self.llm.generate(prompt)

    def _execute_tool(self, node, context):
        # Extract 'action' as the tool name, as defined in your workflow Node config
        tool_name = node.config.get("action")
        params = node.config.get("params", {})
        if not tool_name:
            raise ValueError("Tool node config must specify an 'action'.")
        return self.tool_registry.execute(tool_name, params)
