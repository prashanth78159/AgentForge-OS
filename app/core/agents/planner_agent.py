
from app.core.agents.base_agent import BaseAgent

class PlannerAgent(BaseAgent):

    def run(self, input_text, context):
        prompt =  f'''
You are a planner.

Past memory:
{input_text}

Break into steps.
'''
        return self.llm.generate(prompt)
