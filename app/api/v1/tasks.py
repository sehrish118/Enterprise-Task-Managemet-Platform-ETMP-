import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_permission
from app.core.exceptions import (
    TaskNotFoundError,
    InvalidCredentialsError,
    UserAlreadyAssignedError,
    UserNotFoundError,
)
from app.db.session import get_db
from app.enums.permissions import Permissions
from app.models.user import User
from app.schemas.task import (
    AssignTaskRequest,
    TaskAssigneeRead,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from app.services.task_service import TaskService
import math

from app.schemas.pagination import PaginatedResponse


router = APIRouter(
    prefix="/organizations/{organization_id}/projects/{project_id}/tasks",
    tags=["tasks"],
)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    organization_id: uuid.UUID,
    project_id: uuid.UUID,
    payload: TaskCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.TASK_CREATE))],
) -> TaskRead:
    service = TaskService(db)
    # try:
    task = await service.create_task(
        organization_id=organization_id,
        project_id=project_id,
        status_id=payload.status_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        parent_task_id=payload.parent_task_id,
        due_date=payload.due_date,
        created_by=current_user.id,
    )
    # except TaskStatusNotFoundError as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
    #     ) from e
    return TaskRead.model_validate(task)


@router.get("", response_model=PaginatedResponse[TaskRead])
async def list_tasks(
    organization_id: uuid.UUID,
    project_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    status_id: uuid.UUID | None = None,
    priority: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[TaskRead]:
    service = TaskService(db)
    tasks, total = await service.list_tasks(
        project_id,
        status_id=status_id,
        priority=priority,
        search=search,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[TaskRead.model_validate(t) for t in tasks],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0,
    )


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    organization_id: uuid.UUID,
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskRead:
    service = TaskService(db)
    # try:
    task = await service.get_task(task_id)
    # except TaskNotFoundError as e:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return TaskRead.model_validate(task)


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    organization_id: uuid.UUID,
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    payload: TaskUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.TASK_UPDATE))],
) -> TaskRead:
    service = TaskService(db)
    # try:
    task = await service.update_task(
        task_id=task_id,
        title=payload.title,
        description=payload.description,
        status_id=payload.status_id,
        priority=payload.priority,
        due_date=payload.due_date,
    )
    # except TaskNotFoundError as e:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    # except TaskStatusNotFoundError as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
    #     ) from e
    return TaskRead.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    organization_id: uuid.UUID,
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = TaskService(db)
    try:
        await service.delete_task(task_id, requesting_user_id=current_user.id)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e


@router.post(
    "/{task_id}/assignees",
    response_model=TaskAssigneeRead,
    status_code=status.HTTP_201_CREATED,
)
async def assign_task(
    organization_id: uuid.UUID,
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    payload: AssignTaskRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskAssigneeRead:
    service = TaskService(db)
    try:
        assignee = await service.assign_user(
            organization_id=organization_id,
            task_id=task_id,
            email=payload.email,
            requesting_user_id=current_user.id,
        )
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except (UserAlreadyAssignedError, InvalidCredentialsError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e

    from app.repositories.user_repository import UserRepository

    user = await UserRepository(db).get_by_id(assignee.user_id)
    full_name = user.full_name if user else "Unknown User"

    return TaskAssigneeRead(
        id=assignee.id, user_id=assignee.user_id, user_full_name=full_name
    )


@router.get("/{task_id}/assignees", response_model=list[TaskAssigneeRead])
async def list_task_assignees(
    organization_id: uuid.UUID,
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[TaskAssigneeRead]:
    service = TaskService(db)
    try:
        assignees_with_names = await service.list_assignees_with_names(task_id)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return [
        TaskAssigneeRead(id=a.id, user_id=a.user_id, user_full_name=name)
        for a, name in assignees_with_names
    ]
