import uuid
from datetime import datetime

from pydantic import BaseModel


class MyTaskSummary(BaseModel):
    id: uuid.UUID
    title: str
    priority: str
    due_date: datetime | None
    project_id: uuid.UUID
    status_id: uuid.UUID


class MyDashboard(BaseModel):
    assigned_tasks_count: int
    overdue_tasks_count: int
    unread_notifications_count: int
    recent_tasks: list[MyTaskSummary]


class OrganizationDashboard(BaseModel):
    total_projects: int
    active_projects: int
    total_tasks: int
    total_members: int
    tasks_by_priority: dict[str, int]
