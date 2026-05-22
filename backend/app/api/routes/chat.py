from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import EventSourceResponse

from app.schemas.chat import ChatRequest
from app.services.chat_service import stream_chat_response


router = APIRouter()


@router.post("/chat/stream")
def chat_stream(req: ChatRequest, background_tasks: BackgroundTasks):
    return EventSourceResponse(
        stream_chat_response(req.messages, background_tasks),
        media_type="text/plain",
    )
