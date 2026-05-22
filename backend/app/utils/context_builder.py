from app.schemas.memory import MemoryContext


class ContextBuilder:
    def build(self, memories: MemoryContext) -> str:
        context_parts: list[str] = []

        for memory_id, value in memories.items():
            metadata = value["metadata"]
            context_parts.append(f"""
id: {memory_id}
memory created at: {metadata["created_at"]}
last recalled at: {metadata["modified_at"]}
type: {metadata["type"]}

{value["content"]}
\n\n
""")
        return "".join(context_parts)
