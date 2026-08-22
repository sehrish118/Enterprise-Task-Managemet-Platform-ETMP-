import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task_status import TaskStatus


class TaskStatusRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, status_id: uuid.UUID) -> TaskStatus | None:
        result = await self.session.execute(
            select(TaskStatus).where(
                TaskStatus.id == status_id, TaskStatus.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name(
        self, *, organization_id: uuid.UUID, name: str
    ) -> TaskStatus | None:
        result = await self.session.execute(
            select(TaskStatus).where(
                TaskStatus.organization_id == organization_id,
                TaskStatus.name == name,
                TaskStatus.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self, *, organization_id: uuid.UUID, name: str, color: str, position: int
    ) -> TaskStatus:
        status = TaskStatus(
            organization_id=organization_id, name=name, color=color, position=position
        )
        self.session.add(status)
        await self.session.flush()
        return status

    async def list_by_organization(
        self, organization_id: uuid.UUID
    ) -> list[TaskStatus]:
        result = await self.session.execute(
            select(TaskStatus)
            .where(
                TaskStatus.organization_id == organization_id,
                TaskStatus.deleted_at.is_(None),
            )
            .order_by(TaskStatus.position)
        )
        return list(result.scalars().all())
