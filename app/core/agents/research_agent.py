
from app.core.agents.base_agent import BaseAgent

class ResearchAgent(BaseAgent):

    def run(self, input_text, context):
        prompt = f'''
Research the following topic deeply:

{input_text}
'''
        return self.llm.generate(prompt)
