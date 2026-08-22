import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_permission
from app.core.exceptions import TaskStatusAlreadyExistsError
from app.db.session import get_db
from app.enums.permissions import Permissions
from app.schemas.task import TaskStatusCreate, TaskStatusRead
from app.services.task_status_service import TaskStatusService

router = APIRouter(
    prefix="/organizations/{organization_id}/task-statuses", tags=["task-statuses"]
)


@router.post("", response_model=TaskStatusRead, status_code=status.HTTP_201_CREATED)
async def create_task_status(
    organization_id: uuid.UUID,
    payload: TaskStatusCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.PROJECT_MANAGE_MEMBERS))],
) -> TaskStatusRead:
    service = TaskStatusService(db)
    # try:
    result = await service.create_status(
        organization_id=organization_id,
        name=payload.name,
        color=payload.color,
        position=payload.position,
    )
    # except TaskStatusAlreadyExistsError as e:
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    return TaskStatusRead.model_validate(result)


@router.get("", response_model=list[TaskStatusRead])
async def list_task_statuses(
    organization_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[TaskStatusRead]:
    service = TaskStatusService(db)
    statuses = await service.list_statuses(organization_id)
    return [TaskStatusRead.model_validate(s) for s in statuses]
