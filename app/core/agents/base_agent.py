
from app.services.llm_service import LLMService # Import LLMService
from app.core.metrics.metrics_manager import MetricsManager # Import MetricsManager

class BaseAgent:

    def __init__(self, name: str, llm_service: LLMService, metrics_manager: MetricsManager = None):
        self.name = name
        self.llm_service = llm_service
        self.metrics_manager = metrics_manager

    def run(self, input_text: str, context: dict):
        raise NotImplementedError

    def _generate_and_log(self, prompt: str, memory_context: str = ""):
        import time
        start_time = time.time()
        response_content, prompt_tokens, completion_tokens, total_cost = self.llm_service.generate(prompt, memory_context)
        duration = time.time() - start_time

        if self.metrics_manager:
            self.metrics_manager.log_step_metrics(
                step_name=self.name,
                llm_response_content=response_content,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_cost=total_cost,
                duration=duration
            )
        return response_content
