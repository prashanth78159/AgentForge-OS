
class StateManager:
    def __init__(self):
        self.storage = {}

    def get(self, execution_id):
        return self.storage.get(execution_id, {})

    def set(self, execution_id, state):
        self.storage[execution_id] = state

    def update(self, execution_id, key, value):
        self.storage.setdefault(execution_id, {})
        self.storage[execution_id][key] = value
