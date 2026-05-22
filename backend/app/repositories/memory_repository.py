import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

from app.core.constants import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PORT,
    DEFAULT_MEMORY_RESULT_COUNT,
    MEMORY_EMBEDDING_MODEL,
    OLLAMA_EMBEDDING_URL,
)
from app.schemas.memory import MemoryContext, MemoryMetadata


class MemoryRepository:
    def __init__(self):
        embedding_function = OllamaEmbeddingFunction(
            model_name=MEMORY_EMBEDDING_MODEL,
            url=OLLAMA_EMBEDDING_URL,
        )

        self.client = chromadb.HttpClient(port=CHROMA_PORT)
        self.collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            embedding_function=embedding_function,
        )

    def upsert(
        self,
        ids: list[str],
        contents: list[str],
        metadatas: list[MemoryMetadata] | None = None,
    ) -> None:
        self.collection.upsert(
            ids=ids,
            documents=contents,
            metadatas=metadatas or [],
        )

    def _build_context(self, res: dict[str, list]) -> MemoryContext:
        memories: MemoryContext = {}

        for ids, documents, metadatas in zip(
            res["ids"], res["documents"], res["metadatas"]
        ):
            for memory_id, document, metadata in zip(ids, documents, metadatas):
                memories[memory_id] = {"content": document, "metadata": metadata}

        return memories

    def retrieve(
        self,
        queries: list[str],
        metadatas: list[MemoryMetadata] | None = None,
    ) -> MemoryContext:
        if not metadatas:
            res = self.collection.query(
                query_texts=queries,
                n_results=DEFAULT_MEMORY_RESULT_COUNT,
            )

            return self._build_context(res)

        else:
            res = self.collection.query(
                query_texts=queries,
                n_results=DEFAULT_MEMORY_RESULT_COUNT,
            )

            return self._build_context(res)
