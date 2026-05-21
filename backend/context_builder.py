class ContextBuilder:
    def __init__(self):
        pass

    def build(self, memories: dict):
        context = ""

        for id, value in memories.items():
            context += f"""
id: {id}
memory created at: {value["metadata"]["created_at"]}
last recalled at: {value["metadata"]["modified_at"]}
type: {value["metadata"]["type"]}

{value["content"]}
\n\n
"""
        return context