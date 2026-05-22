from langchain_ollama import ChatOllama

from app.core.config import settings
from app.core.constants import CHAT_MODEL, OLLAMA_BASE_URL


base_ollama = ChatOllama(
    model=CHAT_MODEL,
    reasoning=True,
    base_url=OLLAMA_BASE_URL,
    client_kwargs={
        "headers": {"Authorization": f"Bearer {settings.ollama_api_key}"},
    },
)


def bind_ollama_tools(tools: list):
    return base_ollama.bind_tools(tools)
