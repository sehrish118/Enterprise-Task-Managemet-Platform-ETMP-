import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    type_id: uuid.UUID
    title: str
    message: str
    entity_type: str
    entity_id: uuid.UUID
    is_read: bool
    created_at: datetime
