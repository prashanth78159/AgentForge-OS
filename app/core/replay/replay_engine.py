
class ReplayEngine:

    def __init__(self, store):
        self.store = store

    def replay(self, execution_id):
        logs = self.store.get(execution_id)

        print(f"Replaying Execution: {execution_id}") # Removed emoji

        for log in logs:
            print("--- STEP ---") # Removed leading newline, let print add its own.
            print(f"Step: {log['step']}") # Using f-string for consistency and clarity
            print(f"Input: {str(log['input'])[:100]}") # Using f-string
            print(f"Output: {str(log['output'])[:100]}") # Using f-string

        return logs
