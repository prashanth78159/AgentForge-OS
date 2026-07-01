
from app.core.agents.base_agent import BaseAgent

class WriterAgent(BaseAgent):

    def run(self, input_text, context):
        prompt = f'''
Use this context:

{input_text}

Generate a high-quality answer.
'''
        return self.llm.generate(prompt)
