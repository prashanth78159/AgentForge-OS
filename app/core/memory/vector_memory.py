
class VectorMemory:

    def __init__(self):
        self.store = []

    def add(self, text):
        self.store.append(text)

    def search(self, query):
        # SIMPLE similarity (placeholder)
        results = []
        for item in self.store:
            if any(word in item.lower() for word in query.lower().split()):
                results.append(item)
        return results[:3]
