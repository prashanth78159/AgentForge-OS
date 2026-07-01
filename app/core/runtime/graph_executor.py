
import networkx as nx

class GraphExecutor:

    def __init__(self, workflow):
        self.graph = nx.DiGraph()

        for node in workflow.nodes:
            self.graph.add_node(node.id, data=node)

        for edge in workflow.edges:
            self.graph.add_edge(edge.source, edge.target)

    def get_execution_order(self):
        return list(nx.topological_sort(self.graph))

    def get_levels(self):
        # ✅ NEW METHOD FOR PARALLEL EXECUTION
        return list(nx.topological_generations(self.graph))
