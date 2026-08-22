import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import TaskStatusAlreadyExistsError
from app.models.task_status import TaskStatus
from app.repositories.task_status_repository import TaskStatusRepository


class TaskStatusService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.status_repo = TaskStatusRepository(session)

    async def create_status(
        self, *, organization_id: uuid.UUID, name: str, color: str, position: int
    ) -> TaskStatus:
        existing = await self.status_repo.get_by_name(
            organization_id=organization_id, name=name
        )
        if existing is not None:
            raise TaskStatusAlreadyExistsError(
                f"Status '{name}' already exists in this organization"
            )
        status = await self.status_repo.create(
            organization_id=organization_id, name=name, color=color, position=position
        )
        await self.session.commit()
        return status

    async def list_statuses(self, organization_id: uuid.UUID) -> list[TaskStatus]:
        return await self.status_repo.list_by_organization(organization_id)
