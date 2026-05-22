import uuid

from app.core.constants import MEMORY_EXTRACTION_PROMPT
from app.repositories.memory_repository import MemoryRepository
from app.schemas.memory import MemoryMetadata
from app.services.llm_service import base_ollama
from app.utils.datetime import utc_now_iso


memory_repository = MemoryRepository()


def build_memory_metadata() -> MemoryMetadata:
    now = utc_now_iso()
    return {"created_at": now, "modified_at": now, "type": "episodic"}


def save_memory(messages: list[str]) -> None:
    [human, ai] = messages

    sanitized_messages = [
        ("system", MEMORY_EXTRACTION_PROMPT),
        (
            "human",
            f"""
            human: {human}

            ai: {ai}
            """,
        ),
    ]

    resp = base_ollama.invoke(input=sanitized_messages)
    observations = resp.content.split("\n")

    ids, contents, metadatas = [], [], []

    for obv in observations:
        sanitized_obv = obv.strip()

        if len(sanitized_obv) != 0:
            ids.append(str(uuid.uuid4()))
            contents.append(sanitized_obv)
            metadatas.append(build_memory_metadata())

    print(ids, contents, metadatas)

    memory_repository.upsert(ids, contents, metadatas)
