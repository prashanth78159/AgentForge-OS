
from app.core.agents.base_agent import BaseAgent

class CriticAgent(BaseAgent):

    def run(self, input_text, context):
        prompt = f'''
Critically evaluate and improve this output:

{input_text}
'''
        return self.llm.generate(prompt)
