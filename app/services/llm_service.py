
import os
from groq import Groq
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai


class LLMService:

    print("LLMService loaded - v4 ✅")

    AVAILABLE_MODELS = {
        "Groq": ["llama-3.1-8b-instant", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
        "OpenAI": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
        "Anthropic": ["claude-3-haiku-20240307", "claude-3-sonnet-20240229"],
        "Gemini": ["gemini-1.5-flash", "gemini-1.5-pro"],
        "Deepseek": ["deepseek-chat", "deepseek-coder"],
        "OpenRouter": ["mistralai/mistral-7b-instruct:free", "openai/gpt-3.5-turbo", "google/gemini-pro"]
    }

    TOKENS_PER_WORD = 1.5
    MAX_CONTEXT_WINDOW_TOKENS = 8000
    MAX_INPUT_TOKENS = 7000

    MODEL_COSTS = {
        "Groq": {"llama-3.1-8b-instant": {"input": 0.0001, "output": 0.0001}},
        "OpenAI": {"gpt-4o-mini": {"input": 0.00015, "output": 0.0006}},
        "Anthropic": {"claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125}},
        "Gemini": {"gemini-1.5-flash": {"input": 0.00035, "output": 0.00105}},
        "Deepseek": {"deepseek-chat": {"input": 0.0001, "output": 0.0002}},
        "OpenRouter": {"mistralai/mistral-7b-instruct:free": {"input": 0.0, "output": 0.0}}
    }

    def __init__(self, llm_provider: str, api_key: str, model_name: str):
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.client = None

        if not api_key:
            raise ValueError(f"API key missing for {llm_provider}")

        if llm_provider == "Groq":
            self.client = Groq(api_key=api_key)

        elif llm_provider == "OpenAI":
            self.client = OpenAI(api_key=api_key)

        elif llm_provider == "Anthropic":
            self.client = Anthropic(api_key=api_key)

        elif llm_provider == "Gemini":
            genai.configure(api_key=api_key)

        elif llm_provider == "Deepseek":
            self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")

        elif llm_provider == "OpenRouter":
            self.client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

        else:
            raise ValueError(f"Unsupported provider: {llm_provider}")

        models = self.AVAILABLE_MODELS.get(llm_provider)
        if not models:
            raise ValueError(f"No models available for {llm_provider}")

        if model_name not in models:
            print(f"⚠️ Model {model_name} not found. Using default {models[0]}")
            self.model_name = models[0]

    def _estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        return int(len(text.split()) * self.TOKENS_PER_WORD)

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        costs = self.MODEL_COSTS.get(self.llm_provider, {}).get(self.model_name, {})
        input_cost = costs.get("input", 0.0)
        output_cost = costs.get("output", 0.0)

        total = (prompt_tokens / 1000) * input_cost + (completion_tokens / 1000) * output_cost
        return round(total, 6)

    def _summarize_text_for_context(self, text: str, max_tokens: int) -> str:
        if self._estimate_tokens(text) <= max_tokens:
            return text

        words = text.split()
        keep = int(max_tokens / self.TOKENS_PER_WORD) - 50

        if keep <= 0:
            return "[Context too large]"

        truncated = " ".join(words[:keep])
        return "[TRUNCATED] " + truncated

    def generate(self, prompt: str, memory_context: str = ""):

        print(f"DEBUG → {self.llm_provider} | {self.model_name}")

        full_prompt = prompt

        if memory_context:
            est_prompt = self._estimate_tokens(prompt)
            available = self.MAX_INPUT_TOKENS - est_prompt - 200

            if available < 0:
                available = 0

            memory = self._summarize_text_for_context(memory_context, available)
            # Escape double quotes in dynamic parts to prevent SyntaxError
            full_prompt = "Context:"
            full_prompt += "\n" + memory.replace('"', '\"') + "\n\n" + prompt.replace('"', '\"')

        try:
            max_output = self.MAX_CONTEXT_WINDOW_TOKENS - self._estimate_tokens(full_prompt)
            if max_output < 50:
                max_output = 50

            prompt_tokens = self._estimate_tokens(full_prompt)

            if self.llm_provider in ["Groq", "OpenAI", "Deepseek", "OpenRouter"]:

                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": full_prompt}],
                    max_tokens=max_output
                )

                output = response.choices[0].message.content

                if response.usage:
                    prompt_tokens = response.usage.prompt_tokens
                    completion_tokens = response.usage.completion_tokens
                else:
                    completion_tokens = self._estimate_tokens(output)

            elif self.llm_provider == "Anthropic":

                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=max_output,
                    messages=[{"role": "user", "content": full_prompt}]
                )

                output = response.content[0].text
                prompt_tokens = self._estimate_tokens(full_prompt)
                completion_tokens = self._estimate_tokens(output)

            elif self.llm_provider == "Gemini":

                model = genai.GenerativeModel(self.model_name)
                response = model.generate_content(full_prompt)

                output = response.text
                prompt_tokens = self._estimate_tokens(full_prompt)
                completion_tokens = self._estimate_tokens(output)

            else:
                raise ValueError("Unsupported provider")

            cost = self._calculate_cost(prompt_tokens, completion_tokens)

            return output, prompt_tokens, completion_tokens, cost

        except Exception as e:
            if "413" in str(e) or "too large" in str(e):
                return "[Error: Request too large]", 0, 0, 0.0
            raise

    @classmethod
    def get_available_models(cls):
        return cls.AVAILABLE_MODELS

    @classmethod
    def get_default_model(cls, provider: str):
        models = cls.AVAILABLE_MODELS.get(provider)
        return models[0] if models else None
