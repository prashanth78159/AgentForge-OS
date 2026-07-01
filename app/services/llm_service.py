
from groq import Groq

class LLMService:

    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def generate(self, prompt: str):
        model_name = "llama-3.1-8b-instant" # Updated model to llama3-8b-8192
        print(f"DEBUG: Attempting to generate with model: {model_name}") # Added for debugging
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content
