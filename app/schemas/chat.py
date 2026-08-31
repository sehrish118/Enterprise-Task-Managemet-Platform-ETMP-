# app/schemas/chat.py
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.chat_message import ChatMessageRole


class ChatRequest(BaseModel):
    message: str
    session_id: uuid.UUID | None = None  # None = start a new session


class ChatMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: ChatMessageRole
    content: str
    created_at: datetime


class ChatResponse(BaseModel):
    reply: str
    session_id: uuid.UUID


class ChatSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime


class ChatSessionWithMessages(ChatSessionRead):
    messages: list[ChatMessageRead]
