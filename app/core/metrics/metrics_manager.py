
import time
from typing import List, Dict, Any

class MetricsManager:

    def __init__(self):
        self.execution_metrics: Dict[str, List[Dict[str, Any]]] = {}
        self.current_execution_id: str = None

    def start_execution(self, execution_id: str):
        self.current_execution_id = execution_id
        self.execution_metrics[execution_id] = []

    def log_step_metrics(self, step_name: str, llm_response_content: str, prompt_tokens: int, completion_tokens: int, total_cost: float, duration: float):
        if not self.current_execution_id:
            print("Warning: MetricsManager not initialized with an execution_id. Call start_execution() first.")
            return

        metrics_entry = {
            "timestamp": time.time(),
            "step_name": step_name,
            "llm_response_content": llm_response_content, # Log for context/debugging
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "total_cost": total_cost,
            "duration": duration # Duration for this specific LLM call
        }
        self.execution_metrics[self.current_execution_id].append(metrics_entry)

    def get_metrics(self, execution_id: str = None) -> List[Dict[str, Any]]:
        if execution_id:
            return self.execution_metrics.get(execution_id, [])
        return self.execution_metrics.get(self.current_execution_id, [])

    def get_all_executions_metrics(self) -> Dict[str, List[Dict[str, Any]]]:
        return self.execution_metrics

    def clear_metrics(self, execution_id: str = None):
        if execution_id:
            if execution_id in self.execution_metrics:
                del self.execution_metrics[execution_id]
        else:
            self.execution_metrics = {}
        self.current_execution_id = None

