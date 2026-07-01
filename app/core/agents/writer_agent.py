
from app.core.agents.base_agent import BaseAgent

class WriterAgent(BaseAgent):

    def run(self, input_text: str, context: dict):
        prompt = f'''
You are a skilled content writer. Your goal is to produce high-quality, engaging content based on the provided research or draft.

Here is the context or draft:
{input_text}

Craft a well-structured and polished piece of writing.
'''
        return self._generate_and_log(prompt)
