
from app.core.agents.base_agent import BaseAgent

class PlannerAgent(BaseAgent):

    def run(self, input_text: str, context: dict):
        prompt =  f'''
You are a planner. Your goal is to break down complex tasks into a sequence of actionable steps.

Here's the overall task and any relevant memory:
{input_text}

Provide a clear, concise plan with numbered steps.
'''
        return self._generate_and_log(prompt)
