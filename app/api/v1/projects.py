# import uuid
# from typing import Annotated

# from fastapi import APIRouter, Depends, status
# from sqlalchemy.ext.asyncio import AsyncSession
# from fastapi import HTTPException
# from app.api.dependencies import get_current_user, require_permission
# from app.db.session import get_db
# from app.enums.permissions import Permissions
# from app.models.user import User
# from app.schemas.project import (
#     AddProjectMemberRequest,
#     ProjectCreate,
#     ProjectMemberRead,
#     ProjectRead,
#     ProjectUpdate,
# )
# from app.services.project_service import ProjectService
# from app.core.exceptions import (
#     ProjectNotFoundError,
#     UserAlreadyProjectMemberError,
#     UserNotFoundError,
#     UserNotOrganizationMemberError,
#     ProjectNameAlreadyExistsError,
#     ProjectMemberNotFoundError,
# )


# router = APIRouter(
#     prefix="/organizations/{organization_id}/projects", tags=["projects"]
# )


# @router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
# async def create_project(
#     organization_id: uuid.UUID,
#     payload: ProjectCreate,
#     current_user: Annotated[User, Depends(get_current_user)],
#     db: Annotated[AsyncSession, Depends(get_db)],
#     _: Annotated[None, Depends(require_permission(Permissions.PROJECT_CREATE))],
# ) -> ProjectRead:
#     service = ProjectService(db)
#     try:
#         project = await service.create_project(
#             organization_id=organization_id,
#             name=payload.name,
#             created_by=current_user.id,
#         )
#     except ProjectNameAlreadyExistsError as e:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
#     return ProjectRead.model_validate(project)


# @router.get("", response_model=list[ProjectRead])
# async def list_projects(
#     organization_id: uuid.UUID,
#     current_user: Annotated[User, Depends(get_current_user)],
#     db: Annotated[AsyncSession, Depends(get_db)],
# ) -> list[ProjectRead]:
#     service = ProjectService(db)
#     projects = await service.list_projects(
#         organization_id=organization_id, requesting_user_id=current_user.id
#     )
#     return [ProjectRead.model_validate(p) for p in projects]


# @router.get("/{project_id}", response_model=ProjectRead)
# async def get_project(
#     organization_id: uuid.UUID,
#     project_id: uuid.UUID,
#     current_user: Annotated[User, Depends(get_current_user)],
#     db: Annotated[AsyncSession, Depends(get_db)],
# ) -> ProjectRead:
#     service = ProjectService(db)
#     try:
#         project = await service.get_project(
#             project_id,
#             requesting_user_id=current_user.id,
#             organization_id=organization_id,
#         )
#     except ProjectNotFoundError as e:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
#     return ProjectRead.model_validate(project)


# @router.patch("/{project_id}", response_model=ProjectRead)
# async def update_project(
#     organization_id: uuid.UUID,
#     project_id: uuid.UUID,
#     payload: ProjectUpdate,
#     current_user: Annotated[User, Depends(get_current_user)],
#     db: Annotated[AsyncSession, Depends(get_db)],
#     _: Annotated[None, Depends(require_permission(Permissions.PROJECT_MANAGE_MEMBERS))],
# ) -> ProjectRead:
#     service = ProjectService(db)
#     try:
#         project = await service.update_project(
#             project_id=project_id,
#             name=payload.name,
#             status=payload.status,
#             is_archived=payload.is_archived,
#             requesting_user_id=current_user.id,
#             organization_id=organization_id,
#         )
#     except ProjectNotFoundError as e:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
#     return ProjectRead.model_validate(project)


# @router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_project(
#     organization_id: uuid.UUID,
#     project_id: uuid.UUID,
#     current_user: Annotated[User, Depends(get_current_user)],
#     db: Annotated[AsyncSession, Depends(get_db)],
#     _: Annotated[None, Depends(require_permission(Permissions.PROJECT_DELETE))],
# ) -> None:
#     service = ProjectService(db)
#     try:
#         await service.delete_project(
#             project_id,
#             requesting_user_id=current_user.id,
#             organization_id=organization_id,
#         )
#     except ProjectNotFoundError as e:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


# @router.post(
#     "/{project_id}/members",
#     response_model=ProjectMemberRead,
#     status_code=status.HTTP_201_CREATED,
# )
# async def add_project_member(
#     organization_id: uuid.UUID,
#     project_id: uuid.UUID,
#     payload: AddProjectMemberRequest,
#     current_user: Annotated[User, Depends(get_current_user)],
#     db: Annotated[AsyncSession, Depends(get_db)],
#     _: Annotated[None, Depends(require_permission(Permissions.PROJECT_MANAGE_MEMBERS))],
# ) -> ProjectMemberRead:
#     service = ProjectService(db)
#     try:
#         member = await service.add_member(
#             organization_id=organization_id,
#             project_id=project_id,
#             user_id=payload.user_id,
#             role=payload.role,
#             requesting_user_id=current_user.id,
#         )
#     except ProjectNotFoundError as e:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
#     except UserNotFoundError as e:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
#     except (UserAlreadyProjectMemberError, UserNotOrganizationMemberError) as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
#         ) from e

#     from app.repositories.user_repository import UserRepository

#     user = await UserRepository(db).get_by_id(member.user_id)
#     full_name = user.full_name if user else "Unknown User"

#     return ProjectMemberRead(
#         id=member.id,
#         user_id=member.user_id,
#         user_full_name=full_name,
#         role=member.role.value,
#     )


# @router.get("/{project_id}/members", response_model=list[ProjectMemberRead])
# async def list_project_members(
#     organization_id: uuid.UUID,
#     project_id: uuid.UUID,
#     current_user: Annotated[User, Depends(get_current_user)],
#     db: Annotated[AsyncSession, Depends(get_db)],
# ) -> list[ProjectMemberRead]:
#     service = ProjectService(db)
#     try:
#         members = await service.list_members_with_names(
#             project_id,
#             requesting_user_id=current_user.id,
#             organization_id=organization_id,
#         )
#     except ProjectNotFoundError as e:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

#     return [
#         ProjectMemberRead(
#             id=m.id, user_id=m.user_id, user_full_name=name, role=m.role.value
#         )
#         for m, name in members
#     ]


# # app/api/v1/projects.py


# @router.delete(
#     "/{project_id}/members/{user_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
# )
# async def remove_project_member(
#     organization_id: uuid.UUID,
#     project_id: uuid.UUID,
#     user_id: uuid.UUID,
#     current_user: Annotated[User, Depends(get_current_user)],
#     db: Annotated[AsyncSession, Depends(get_db)],
#     _: Annotated[None, Depends(require_permission(Permissions.PROJECT_MANAGE_MEMBERS))],
# ) -> None:
#     service = ProjectService(db)
#     try:
#         await service.remove_member(
#             organization_id=organization_id,
#             project_id=project_id,
#             user_id=user_id,
#             requesting_user_id=current_user.id,
#         )
#     except (ProjectMemberNotFoundError, ProjectNotFoundError) as e:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_permission
from app.core.exceptions import (
    ProjectMemberNotFoundError,
    ProjectNameAlreadyExistsError,
    ProjectNotFoundError,
    UserAlreadyProjectMemberError,
    UserNotFoundError,
    UserNotOrganizationMemberError,
)
from app.db.session import get_db
from app.enums.permissions import Permissions
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.project import (
    AddProjectMemberRequest,
    ProjectCreate,
    ProjectMemberRead,
    ProjectRead,
    ProjectUpdate,
)
from app.services.project_service import ProjectService

router = APIRouter(
    prefix="/organizations/{organization_id}/projects", tags=["projects"]
)


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    organization_id: uuid.UUID,
    payload: ProjectCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.PROJECT_CREATE))],
) -> ProjectRead:
    service = ProjectService(db)
    try:
        project = await service.create_project(
            organization_id=organization_id,
            name=payload.name,
            created_by=current_user.id,
        )
    except ProjectNameAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    return ProjectRead.model_validate(project)


@router.get("", response_model=list[ProjectRead])
async def list_projects(
    organization_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ProjectRead]:
    service = ProjectService(db)
    projects = await service.list_projects(
        organization_id=organization_id, requesting_user_id=current_user.id
    )
    return [ProjectRead.model_validate(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    organization_id: uuid.UUID,
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProjectRead:
    service = ProjectService(db)
    try:
        project = await service.get_project(
            project_id,
            requesting_user_id=current_user.id,
            organization_id=organization_id,
        )
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return ProjectRead.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    organization_id: uuid.UUID,
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.PROJECT_MANAGE_MEMBERS))],
) -> ProjectRead:
    service = ProjectService(db)
    try:
        project = await service.update_project(
            project_id=project_id,
            name=payload.name,
            status=payload.status,
            is_archived=payload.is_archived,
            requesting_user_id=current_user.id,
            organization_id=organization_id,
        )
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return ProjectRead.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    organization_id: uuid.UUID,
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.PROJECT_DELETE))],
) -> None:
    service = ProjectService(db)
    try:
        await service.delete_project(
            project_id,
            requesting_user_id=current_user.id,
            organization_id=organization_id,
        )
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_project_member(
    organization_id: uuid.UUID,
    project_id: uuid.UUID,
    payload: AddProjectMemberRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.PROJECT_MANAGE_MEMBERS))],
) -> ProjectMemberRead:
    service = ProjectService(db)
    try:
        member = await service.add_member(
            organization_id=organization_id,
            project_id=project_id,
            user_id=payload.user_id,
            role=payload.role,
            requesting_user_id=current_user.id,
        )
    except (ProjectNotFoundError, UserNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except (UserAlreadyProjectMemberError, UserNotOrganizationMemberError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e

    user = await UserRepository(db).get_by_id(member.user_id)
    full_name = user.full_name if user else "Unknown User"

    return ProjectMemberRead(
        id=member.id,
        user_id=member.user_id,
        user_full_name=full_name,
        role=member.role.value,
    )


@router.get("/{project_id}/members", response_model=list[ProjectMemberRead])
async def list_project_members(
    organization_id: uuid.UUID,
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ProjectMemberRead]:
    service = ProjectService(db)
    try:
        members = await service.list_members_with_names(
            project_id,
            requesting_user_id=current_user.id,
            organization_id=organization_id,
        )
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    return [
        ProjectMemberRead(
            id=m.id, user_id=m.user_id, user_full_name=name, role=m.role.value
        )
        for m, name in members
    ]


@router.delete(
    "/{project_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_project_member(
    organization_id: uuid.UUID,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.PROJECT_MANAGE_MEMBERS))],
) -> None:
    service = ProjectService(db)
    try:
        await service.remove_member(
            organization_id=organization_id,
            project_id=project_id,
            user_id=user_id,
            requesting_user_id=current_user.id,
        )
    except (ProjectMemberNotFoundError, ProjectNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
