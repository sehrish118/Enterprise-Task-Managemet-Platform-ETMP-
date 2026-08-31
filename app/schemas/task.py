# import uuid
# from datetime import datetime

# from pydantic import BaseModel, ConfigDict, Field


# class TaskCreate(BaseModel):
#     title: str = Field(min_length=1, max_length=255)
#     description: str | None = None
#     status_id: uuid.UUID
#     priority: str = Field(default="MEDIUM", description="LOW, MEDIUM, HIGH, URGENT")
#     parent_task_id: uuid.UUID | None = None
#     due_date: datetime | None = None


# class TaskUpdate(BaseModel):
#     title: str | None = Field(default=None, min_length=1, max_length=255)
#     description: str | None = None
#     status_id: uuid.UUID | None = None
#     priority: str | None = None
#     due_date: datetime | None = None


# class TaskRead(BaseModel):
#     model_config = ConfigDict(from_attributes=True)
#     id: uuid.UUID
#     organization_id: uuid.UUID
#     project_id: uuid.UUID
#     parent_task_id: uuid.UUID | None
#     status_id: uuid.UUID
#     title: str
#     description: str | None
#     priority: str
#     due_date: datetime | None
#     created_by: uuid.UUID
#     created_at: datetime


# class AssignTaskRequest(BaseModel):
#     email: str


# class TaskAssigneeRead(BaseModel):
#     model_config = ConfigDict(from_attributes=True)
#     id: uuid.UUID
#     user_id: uuid.UUID
#     user_full_name: str


# class TaskStatusCreate(BaseModel):
#     name: str = Field(min_length=1, max_length=100)
#     color: str = Field(min_length=1, max_length=20)
#     position: int


# class TaskStatusRead(BaseModel):
#     model_config = ConfigDict(from_attributes=True)
#     id: uuid.UUID
#     name: str
#     color: str
#     position: int


import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    status_id: uuid.UUID
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    parent_task_id: Optional[uuid.UUID] = None
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    status_id: uuid.UUID | None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    organization_id: uuid.UUID
    project_id: uuid.UUID
    parent_task_id: Optional[uuid.UUID]
    status_id: uuid.UUID
    title: str
    description: Optional[str]
    priority: TaskPriority
    due_date: Optional[datetime]
    created_by: uuid.UUID
    created_at: datetime


class AssignTaskRequest(BaseModel):
    email: str


class TaskAssigneeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    user_full_name: str
    user_email: Optional[str] = None


class TaskStatusCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    color: str = Field(default="#64748b", min_length=1, max_length=20)
    position: int = Field(default=0)


class TaskStatusRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    color: str
    position: int
