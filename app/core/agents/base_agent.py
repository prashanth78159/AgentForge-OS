
class BaseAgent:

    def __init__(self, name, llm):
        self.name = name
        self.llm = llm

    def run(self, input_text, context):
        raise NotImplementedError
