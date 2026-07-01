
class ExecutionStore:

    def __init__(self):
        self.executions = {}

    def save(self, execution_id, logs):
        self.executions[execution_id] = logs

    def get(self, execution_id):
        return self.executions.get(execution_id, [])
