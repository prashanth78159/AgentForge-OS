
import time

class ExecutionTracer:

    def __init__(self):
        self.logs = []

    def log(self, step, input_data, output_data):
        entry = {
            "step": step,
            "input": input_data,
            "output": output_data,
            "timestamp": time.time()
        }
        self.logs.append(entry)

    def get_logs(self):
        return self.logs
