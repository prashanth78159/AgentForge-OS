
import uuid
import asyncio # Import asyncio at the top level
from app.core.runtime.node_executor import NodeExecutor
from app.core.runtime.graph_executor import GraphExecutor

class ExecutionEngine:

    def __init__(self, event_bus, state_manager, llm_provider: str, api_key: str, model_name: str):
        self.event_bus = event_bus
        self.state_manager = state_manager
        # ❅ Initialize NodeExecutor with LLM parameters
        self.node_executor = NodeExecutor(llm_provider, api_key, model_name)

    async def execute(self, workflow):
        execution_id = str(uuid.uuid4())

        graph_executor = GraphExecutor(workflow)
        levels = graph_executor.get_levels()

        context = {
            "execution_id": execution_id,
            "state": {}
        }

        for level in levels:
            tasks = []

            for node_id in level:
                node = next(n for n in workflow.nodes if n.id == node_id)
                self.event_bus.publish("node_started", {"node_id": node_id})
                tasks.append(self.node_executor.execute(node, context))

            results = await asyncio.gather(*tasks)

            for node_id, result in zip(level, results):
                # Result from node_executor is now a dict: {'output': ..., 'metrics': {...}}
                self.state_manager.update(execution_id, node_id, result)
                self.event_bus.publish("node_completed", {
                    "node_id": node_id,
                    "result": result
                })

        return self.state_manager.get(execution_id)
