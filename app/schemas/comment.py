import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    content: str = Field(min_length=1)
    parent_comment_id: uuid.UUID | None = None


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1)


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    task_id: uuid.UUID
    user_id: uuid.UUID
    user_full_name: str
    parent_comment_id: uuid.UUID | None
    content: str
    edited_at: datetime | None
    created_at: datetime
