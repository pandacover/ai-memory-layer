from langchain_core.tools import tool
from httpx import ConnectError, ConnectTimeout, TimeoutException

from app.schemas.memory import MemoryMetadata
from app.services.llm_service import bind_ollama_tools
from app.services.memory_service import memory_repository
from app.utils.context_builder import ContextBuilder


memory_context_builder = ContextBuilder()


@tool
def retrieve_memory(
    queries: list[str],
    metadatas: list[MemoryMetadata] | None = None,
) -> str:
    """Retrieve semantic memories."""

    try:
        retrieved_memory = memory_repository.retrieve(queries=queries, metadatas=metadatas)
    except (ConnectError, ConnectTimeout, TimeoutException) as exc:
        return f"Memory retrieval is temporarily unavailable: {exc}"

    memory_context = memory_context_builder.build(memories=retrieved_memory)

    return memory_context


tools = [retrieve_memory]
ollama = bind_ollama_tools(tools)
