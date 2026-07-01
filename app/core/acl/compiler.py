
from app.core.models.workflow import Workflow

class ACLCompiler:

    def compile(self, ast):
        nodes = []
        edges = []

        for node in ast["nodes"]:
            config = {}

            if node["type"] == "llm":
                config["prompt"] = node["args"][0]

            elif node["type"] == "tool":
                config["action"] = node["args"][0] # Changed 'name' to 'action'
                if len(node["args"]) > 1:
                    config["params"] = {"message": node["args"][1]}

            nodes.append({
                "id": node["id"],
                "type": node["type"],
                "config": config
            })

        for edge in ast["edges"]:
            edges.append(edge)

        return Workflow(id=ast["name"], nodes=nodes, edges=edges)
