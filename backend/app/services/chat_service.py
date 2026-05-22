from collections.abc import Iterator

from fastapi import BackgroundTasks

from app.core.constants import SYSTEM_PROMPT
from app.schemas.chat import Message
from app.services.graph_service import graph
from app.services.memory_service import save_memory


def to_langgraph_messages(messages: list[Message]) -> list[dict[str, str]]:
    langgraph_messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for message in messages:
        langgraph_messages.append({"role": message.role, "content": message.content})

    return langgraph_messages


def stream_chat_response(
    messages: list[Message],
    background_tasks: BackgroundTasks,
) -> Iterator[str]:
    langgraph_messages = to_langgraph_messages(messages)
    last_user_content = messages[-1].content
    final_message = ""

    stream = graph.stream_events(
        {
            "messages": langgraph_messages,
        },
        version="v3",
    )

    for message in stream.messages:
        if message.node == "tools":
            print(message.text, end="", flush=True)
        if message.node == "agent":
            for token in message.text:
                final_message += token
                print(token, end="", flush=True)
                yield token
            print()

    if final_message:
        background_tasks.add_task(save_memory, [last_user_content, final_message])
