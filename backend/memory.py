import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

from pydantic import validate_call
from typing import Any

class Memory:
    def __init__(self, ):
        embedding_function = OllamaEmbeddingFunction(model_name="nomic-embed-text:v1.5")

        self.client = chromadb.HttpClient(port=8081)
        self.collection = self.client.get_or_create_collection(name="memories", embedding_function=embedding_function)
    
    
    # @validate_call
    def upsert(self, ids: list[str], contents: list[str], metadatas: list = []):
        self.collection.upsert(
            ids=ids,
            documents=contents,
            metadatas=metadatas
        )

    def _build_context(self, res: dict[list, list, list]):
        mem = dict()

        for ids, documents, metadatas in zip(res["ids"], res["documents"], res["metadatas"]):
            for id, document, metadata in zip(ids, documents, metadatas):
                mem[id] = { "content": document, "metadata": metadata }
        
        return mem

    # @validate_call
    def retrieve(self, queries: list[str], metadatas: list = []):
        if not len(metadatas):
            res = self.collection.query(
                query_texts=queries,
                n_results=5
            )

            return self._build_context(res)
        
        else:
            res = self.collection.query(
                query_texts=queries,
                n_results=5
            )

            return self._build_context(res)
        

        




