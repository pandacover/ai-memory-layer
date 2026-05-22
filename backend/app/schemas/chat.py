from typing import Literal

from pydantic import BaseModel


class Message(BaseModel):
    role: Literal["human", "ai", "system", "tool"]
    content: str
    id: str


class ChatRequest(BaseModel):
    messages: list[Message]
