import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status_id: uuid.UUID
    priority: str = Field(default="MEDIUM", description="LOW, MEDIUM, HIGH, URGENT")
    parent_task_id: uuid.UUID | None = None
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status_id: uuid.UUID | None = None
    priority: str | None = None
    due_date: datetime | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    organization_id: uuid.UUID
    project_id: uuid.UUID
    parent_task_id: uuid.UUID | None
    status_id: uuid.UUID
    title: str
    description: str | None
    priority: str
    due_date: datetime | None
    created_by: uuid.UUID
    created_at: datetime


class AssignTaskRequest(BaseModel):
    email: str


class TaskAssigneeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    user_full_name: str


class TaskStatusCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    color: str = Field(min_length=1, max_length=20)
    position: int


class TaskStatusRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    color: str
    position: int
