import uuid
import os
from typing import Literal

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import EventSourceResponse
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field
from datetime import datetime
from config import settings

from memory import Memory
from context_builder import ContextBuilder

SystemPrompt = """
- the tools you have access to
    - retrieve_memory: uses memories specific to given queries
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

# types
class Message(BaseModel):
    role: Literal["human", "ai", "system", "tool"]
    content: str
    id: str


class ChatRequest(BaseModel):
    messages: list[Message]


# instances
AIMemory = Memory()
AIMemoryContextBuilder = ContextBuilder()

# langgraph

# utils

def save_memory(messages: list[str]):
    [human, ai] = messages

    sanitized_messages = [
        (
            "system",
            """
            You are an expert observer and interpreter. Given a user query, you:
            - infer correct observations limited to the informations provided, and don't overreach
            - return only the observations that should be saved and discard the rest
            - return only observations, separated by lines. No label or markdown is needed. Just plain string.
            - if there's no good observation then you can ignore since you are not obliged to save anything
            - provide distilled 0-N memories out of that given query.

            For example:
            query:
                human: Hey dude, I am Luv. I am a software engineer.
                ai: Hey Luv, nice to meet you.

            good obsverations:
                user name is Luv.
                Luv is a software engineer.
                Luv must like to talk about coding and technology in general.
            
            bad observations:
                user greeted me with (hey dude) so he must be in a jolly mood.
                hey dude is a positive greeting, so user must be a happy person.
            """
        ),
        (
            "human",
            f"""
            human: {human}

            ai: {ai}
            """
        )
    ]

    resp = ollama.invoke(input=sanitized_messages)
    observations = resp.content.split("\n")

    ids, contents, metadatas = [], [], []

    for obv in observations:
        sanitized_obv = obv.strip()

        if len(sanitized_obv) != 0:
            ids.append(str(uuid.uuid4()))
            contents.append(sanitized_obv)
            metadatas.append({ "created_at": datetime.now().isoformat(), "modified_at": datetime.now().isoformat(), "type": "episodic" })
    
    print(ids, contents, metadatas)

    AIMemory.upsert(ids, contents, metadatas)


# tools 

@tool
def retrieve_memory(queries: list[str], metadatas:list[dict] = []):
    """Retrive semantic memories"""

    retrieved_memory = AIMemory.retrieve(queries=queries, metadatas=metadatas)
    memory_context = AIMemoryContextBuilder.build(memories=retrieved_memory) 

    return memory_context


tools = [retrieve_memory]

base_ollama = ChatOllama(model="nemotron-3-super:cloud", reasoning=True, base_url="https://ollama.com", client_kwargs={
    "headers":{ "Authorization": f"Bearer {settings.ollama_api_key}" } 
})
ollama = base_ollama.bind_tools(tools)


# nodes
def agent(state: MessagesState):
    return {"messages": ollama.invoke(state["messages"])}


def should_continue(state: MessagesState):
    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


# builder
builder = StateGraph(MessagesState)
builder.add_node("agent", agent)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_edge("tools", "agent")

graph = builder.compile()


# endpoint
@app.post("/chat/stream")
def chat_stream(req: ChatRequest, background_tasks: BackgroundTasks):
    messages = getattr(req, "messages", [])
    langgraph_messages = []

    langgraph_messages.append({"role": "system", "content": SystemPrompt})

    for message in messages:
        langgraph_messages.append({"role": message.role, "content": message.content})
    
    global last_message
    last_message = messages[-1]

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
            background_tasks.add_task(
                save_memory,
                [last_message.content, final_message]
            )

    return EventSourceResponse(generate_tokens(), media_type="text/plain")
