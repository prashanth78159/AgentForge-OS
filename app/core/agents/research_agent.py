
from app.core.agents.base_agent import BaseAgent

class ResearchAgent(BaseAgent):

    def run(self, input_text: str, context: dict):
        prompt = f'''
You are a research assistant. Your task is to gather detailed information on the given topic.

Here is the topic or question:
{input_text}

Provide a comprehensive summary of your findings.
'''
        return self._generate_and_log(prompt)
