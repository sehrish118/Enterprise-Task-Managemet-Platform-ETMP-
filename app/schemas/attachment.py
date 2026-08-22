import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AttachmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    task_id: uuid.UUID
    uploaded_by: uuid.UUID
    original_filename: str
    mime_type: str
    size: int
    file_url: str
    created_at: datetime
