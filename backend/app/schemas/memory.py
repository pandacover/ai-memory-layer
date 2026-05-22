from typing import TypedDict


MemoryMetadata = dict[str, str]


class MemoryRecord(TypedDict):
    content: str
    metadata: MemoryMetadata


MemoryContext = dict[str, MemoryRecord]
