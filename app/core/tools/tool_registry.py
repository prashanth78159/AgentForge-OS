
class ToolRegistry:

    def __init__(self):
        self.tools = {}

    def register(self, name, func):
        self.tools[name] = func


    def execute(self, name, params):
        if name not in self.tools:
            raise Exception(f"Tool {name} not found")

        return self.tools[name](params)

