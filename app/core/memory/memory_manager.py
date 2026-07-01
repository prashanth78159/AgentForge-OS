
class MemoryManager:

    def __init__(self):
        self.sessions = {}

    def get(self, session_id):
        return self.sessions.get(session_id, [])

    def add(self, session_id, message):
        self.sessions.setdefault(session_id, []).append(message)

    def clear(self, session_id):
        self.sessions[session_id] = []
