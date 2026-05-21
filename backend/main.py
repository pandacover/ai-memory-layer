import uuid
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import EventSourceResponse
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from raw_events import create_table, get_all_raw_events_desc, upsert_raw_event

SystemPrompt = """
- the tools you have access to
    - retrieve_all_tool: retrieves all raw events from the database, including my information
Rules
- never return the raw data retrieved from the tool, ever
- use the tool when you don't know the answer to the question
- use the tool when you are to answer something specific from memory
"""

session_id = str(uuid.uuid4())

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_table()


class Message(BaseModel):
    role: Literal["human", "ai", "system", "tool"]
    content: str
    id: str


class ChatRequest(BaseModel):
    messages: list[Message]

class RetrieveMemoryTool(BaseModel):
    query: str = Field(description="user query")


@tool(args_schema=RetrieveMemoryTool)
def retrieve_all_tool(query: str):
    """Retrieve all raw events from the database."""

    events = get_all_raw_events_desc()

    event_content_vs_words = dict()

    for i, event in enumerate(events):
        event_content_vs_words[event["id"]] = {
            "content": event["content"].split(" "),
            "rank": i 
        }

    query_list = query.split(" ")

    sorted_events = sorted(events, key=lambda event: sum([event_content_vs_words[event["id"]]["content"].count(word) + (len(event_content_vs_words) - event_content_vs_words[event["id"]]["rank"]) for word in query_list]), reverse=True)

    context = """"""

    for i, event in enumerate(sorted_events[:5]):
        context += f"""
            [metadata]
            message_id: {event["id"]}
            author: {event["role"]}
            rank: {i} (lesser is higher)
            modified_at: {event['modified_at']}

            [content]
            {event["content"]}
            
        """
    return context

    


tools = [retrieve_all_tool]

base_ollama = ChatOllama(model="gemma4:e4b", reasoning=True)
ollama = base_ollama.bind_tools(tools)


def agent(state: MessagesState):
    return {"messages": ollama.invoke(state["messages"])}


def should_continue(state: MessagesState):
    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


builder = StateGraph(MessagesState)
builder.add_node("agent", agent)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_edge("tools", "agent")

graph = builder.compile()


@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    messages = getattr(req, "messages", [])
    langgraph_messages = []

    langgraph_messages.append({"role": "system", "content": SystemPrompt})

    for message in messages:
        langgraph_messages.append({"role": message.role, "content": message.content})
    
    last_message = messages[-1]

    upsert_raw_event(
        id=last_message.id if last_message.id else str(uuid.uuid4()),
        role="human",
        content=messages[-1].content,
        session_id=session_id,
    )

    def generate_tokens():
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
            upsert_raw_event(
                id=str(uuid.uuid4()),
                role="ai",
                content=final_message,
                session_id=session_id,
            )

    return EventSourceResponse(generate_tokens(), media_type="text/plain")
