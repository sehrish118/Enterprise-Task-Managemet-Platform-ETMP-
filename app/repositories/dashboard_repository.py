import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.organization_member import OrganizationMember
from app.models.project import Project, ProjectStatus
from app.models.task import Task
from app.models.task_assignee import TaskAssignee


class DashboardRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def count_assigned_tasks(self, user_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Task)
            .join(TaskAssignee, TaskAssignee.task_id == Task.id)
            .where(TaskAssignee.user_id == user_id, Task.deleted_at.is_(None))
        )
        return (await self.session.execute(stmt)).scalar_one()

    async def count_overdue_tasks(self, user_id: uuid.UUID) -> int:
        now = datetime.now(timezone.utc)
        stmt = (
            select(func.count())
            .select_from(Task)
            .join(TaskAssignee, TaskAssignee.task_id == Task.id)
            .where(
                TaskAssignee.user_id == user_id,
                Task.deleted_at.is_(None),
                Task.due_date.is_not(None),
                Task.due_date < now,
            )
        )
        return (await self.session.execute(stmt)).scalar_one()

    async def count_unread_notifications(self, user_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        )
        return (await self.session.execute(stmt)).scalar_one()

    async def recent_assigned_tasks(
        self, user_id: uuid.UUID, *, limit: int = 5
    ) -> list[Task]:
        stmt = (
            select(Task)
            .join(TaskAssignee, TaskAssignee.task_id == Task.id)
            .where(TaskAssignee.user_id == user_id, Task.deleted_at.is_(None))
            .order_by(Task.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_projects(self, organization_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Project)
            .where(
                Project.organization_id == organization_id, Project.deleted_at.is_(None)
            )
        )
        return (await self.session.execute(stmt)).scalar_one()

    async def count_active_projects(self, organization_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Project)
            .where(
                Project.organization_id == organization_id,
                Project.deleted_at.is_(None),
                Project.status == ProjectStatus.ACTIVE,
            )
        )
        return (await self.session.execute(stmt)).scalar_one()

    async def count_tasks(self, organization_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Task)
            .where(Task.organization_id == organization_id, Task.deleted_at.is_(None))
        )
        return (await self.session.execute(stmt)).scalar_one()

    async def count_members(self, organization_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(OrganizationMember)
            .where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.deleted_at.is_(None),
            )
        )
        return (await self.session.execute(stmt)).scalar_one()

    async def tasks_by_priority(self, organization_id: uuid.UUID) -> dict[str, int]:
        stmt = (
            select(Task.priority, func.count())
            .where(Task.organization_id == organization_id, Task.deleted_at.is_(None))
            .group_by(Task.priority)
        )
        result = await self.session.execute(stmt)
        return {priority.value: count for priority, count in result.all()}
