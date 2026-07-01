
from app.core.agents.base_agent import BaseAgent

class CriticAgent(BaseAgent):

    def run(self, input_text: str, context: dict):
        prompt = f'''
You are a critical evaluator. Your role is to analyze the provided output, identify areas for improvement, and suggest concrete revisions.

Here is the output to critique:
{input_text}

Provide a detailed critique and actionable suggestions for improvement.
'''
        return self._generate_and_log(prompt)
