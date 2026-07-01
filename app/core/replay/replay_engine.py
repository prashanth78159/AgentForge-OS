
class ReplayEngine:

    def __init__(self, store):
        self.store = store

    def replay(self, execution_id):
        logs = self.store.get(execution_id)

        print(f"🔁 Replaying Execution: {execution_id}")

        for log in logs:
            print("\n--- STEP ---")
            print("Step:", log["step"])
            print("Input:", str(log["input"])[:100])
            print("Output:", str(log["output"])[:100])

        return logs
