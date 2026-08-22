import uuid
from datetime import datetime, timezone

from sqlalchemy import select, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskPriority
from app.models.task_assignee import TaskAssignee


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, task_id: uuid.UUID) -> Task | None:
        result = await self.session.execute(
            select(Task).where(Task.id == task_id, Task.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        organization_id: uuid.UUID,
        project_id: uuid.UUID,
        status_id: uuid.UUID,
        title: str,
        description: str | None,
        priority: str,
        parent_task_id: uuid.UUID | None,
        due_date: datetime | None,
        created_by: uuid.UUID,
    ) -> Task:
        task = Task(
            organization_id=organization_id,
            project_id=project_id,
            status_id=status_id,
            title=title,
            description=description,
            priority=TaskPriority(priority),
            parent_task_id=parent_task_id,
            due_date=due_date,
            created_by=created_by,
        )
        self.session.add(task)
        await self.session.flush()
        return task

    async def update(
        self,
        task: Task,
        *,
        title: str | None = None,
        description: str | None = None,
        status_id: uuid.UUID | None = None,
        priority: str | None = None,
        due_date: datetime | None = None,
    ) -> Task:
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status_id is not None:
            task.status_id = status_id
        if priority is not None:
            task.priority = TaskPriority(priority)
        if due_date is not None:
            task.due_date = due_date
        await self.session.flush()
        return task

    async def soft_delete(self, task: Task) -> None:
        task.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def list_by_project(
        self,
        project_id: uuid.UUID,
        *,
        status_id: uuid.UUID | None = None,
        priority: str | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Task], int]:
        from sqlalchemy import func, or_

        conditions = [Task.project_id == project_id, Task.deleted_at.is_(None)]
        if status_id is not None:
            conditions.append(Task.status_id == status_id)
        if priority is not None:
            conditions.append(Task.priority == priority)
        if search is not None:
            conditions.append(
                or_(
                    Task.title.ilike(f"%{search}%"),
                    Task.description.ilike(f"%{search}%"),
                )
            )

        count_stmt = select(func.count()).select_from(Task).where(*conditions)
        total = (await self.session.execute(count_stmt)).scalar_one()

        priority_order = case(
            (Task.priority == "URGENT", 1),
            (Task.priority == "HIGH", 2),
            (Task.priority == "MEDIUM", 3),
            (Task.priority == "LOW", 4),
        )

        stmt = (
            select(Task)
            .where(*conditions)
            .order_by(priority_order, Task.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total

    async def assign_user(
        self, *, organization_id: uuid.UUID, task_id: uuid.UUID, user_id: uuid.UUID
    ) -> TaskAssignee:
        assignee = TaskAssignee(
            organization_id=organization_id, task_id=task_id, user_id=user_id
        )
        self.session.add(assignee)
        await self.session.flush()
        return assignee

    async def get_assignment(
        self, *, task_id: uuid.UUID, user_id: uuid.UUID
    ) -> TaskAssignee | None:
        result = await self.session.execute(
            select(TaskAssignee).where(
                TaskAssignee.task_id == task_id, TaskAssignee.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_assignees(self, task_id: uuid.UUID) -> list[TaskAssignee]:
        result = await self.session.execute(
            select(TaskAssignee).where(TaskAssignee.task_id == task_id)
        )
        return list(result.scalars().all())

    async def list_assignees_with_names(
        self, task_id: uuid.UUID
    ) -> list[tuple[TaskAssignee, str]]:
        from sqlalchemy import select as sa_select
        from app.models.user import User

        stmt = (
            sa_select(TaskAssignee, User.full_name)
            .join(User, User.id == TaskAssignee.user_id)
            .where(TaskAssignee.task_id == task_id)
        )
        result = await self.session.execute(stmt)
        return [(assignee, name) for assignee, name in result.all()]
