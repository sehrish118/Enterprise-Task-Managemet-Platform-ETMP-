# # import uuid
# # from typing import Annotated
# # from app.models.user import User
# # from app.repositories.user_repository import UserRepository
# # from fastapi import APIRouter, Depends, HTTPException, status
# # from sqlalchemy.ext.asyncio import AsyncSession
# # from app.api.dependencies import get_current_user
# # from app.api.dependencies import require_permission
# # from app.core.exceptions import (
# #     TeamNotFoundError,
# #     UserAlreadyTeamMemberError,
# #     UserNotFoundError,
# #     UserNotOrganizationMemberError,
# # )
# # from app.db.session import get_db
# # from app.enums.permissions import Permissions
# # from app.schemas.team import (
# #     AddTeamMemberRequest,
# #     TeamCreate,
# #     TeamMemberRead,
# #     TeamRead,
# #     TeamUpdate,
# # )
# # from app.services.team_service import TeamService

# # router = APIRouter(prefix="/organizations/{organization_id}/teams", tags=["teams"])


# # @router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
# # async def create_team(
# #     organization_id: uuid.UUID,
# #     payload: TeamCreate,
# #     db: Annotated[AsyncSession, Depends(get_db)],
# #     _: Annotated[None, Depends(require_permission(Permissions.TEAM_CREATE))],
# # ) -> TeamRead:
# #     service = TeamService(db)
# #     # try:
# #     team = await service.create_team(organization_id=organization_id, name=payload.name)
# #     # except TeamNameAlreadyExistsError as e:
# #     #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
# #     return TeamRead.model_validate(team)


# # @router.get("", response_model=list[TeamRead])
# # async def list_teams(
# #     organization_id: uuid.UUID,
# #     db: Annotated[AsyncSession, Depends(get_db)],
# # ) -> list[TeamRead]:
# #     service = TeamService(db)
# #     teams = await service.list_teams(organization_id)
# #     return [TeamRead.model_validate(t) for t in teams]


# # @router.get("/{team_id}", response_model=TeamRead)
# # async def get_team(
# #     organization_id: uuid.UUID,
# #     team_id: uuid.UUID,
# #     db: Annotated[AsyncSession, Depends(get_db)],
# # ) -> TeamRead:
# #     service = TeamService(db)

# #     # try:
# #     team = await service.get_team(team_id)
# #     # except TeamNotFoundError as e:
# #     #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
# #     return TeamRead.model_validate(team)


# # @router.patch("/{team_id}", response_model=TeamRead)
# # async def update_team(
# #     organization_id: uuid.UUID,
# #     team_id: uuid.UUID,
# #     payload: TeamUpdate,
# #     db: Annotated[AsyncSession, Depends(get_db)],
# #     _: Annotated[None, Depends(require_permission(Permissions.TEAM_MANAGE_MEMBERS))],
# # ) -> TeamRead:
# #     service = TeamService(db)
# #     # try:
# #     team = await service.update_team(team_id=team_id, name=payload.name)
# #     # except TeamNotFoundError as e:
# #     #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
# #     return TeamRead.model_validate(team)


# # @router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
# # async def delete_team(
# #     organization_id: uuid.UUID,
# #     team_id: uuid.UUID,
# #     db: Annotated[AsyncSession, Depends(get_db)],
# #     _: Annotated[None, Depends(require_permission(Permissions.TEAM_DELETE))],
# # ) -> None:
# #     service = TeamService(db)
# #     # try:
# #     await service.delete_team(team_id)
# #     # except TeamNotFoundError as e:
# #     #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


# # @router.post(
# #     "/{team_id}/members",
# #     response_model=TeamMemberRead,
# #     status_code=status.HTTP_201_CREATED,
# # )
# # async def add_team_member(
# #     organization_id: uuid.UUID,
# #     team_id: uuid.UUID,
# #     payload: AddTeamMemberRequest,
# #     current_user: Annotated[User, Depends(get_current_user)],
# #     db: Annotated[AsyncSession, Depends(get_db)],
# #     _: Annotated[None, Depends(require_permission(Permissions.TEAM_MANAGE_MEMBERS))],
# # ) -> TeamMemberRead:
# #     service = TeamService(db)
# #     try:
# #         member = await service.add_member(
# #             organization_id=organization_id,
# #             team_id=team_id,
# #             email=payload.email,
# #             role=payload.role,
# #         )
# #     except TeamNotFoundError as e:
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
# #     except UserNotFoundError as e:
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
# #     except UserAlreadyTeamMemberError as e:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
# #         ) from e

# #     # Fetch the user's name separately — avoids the lazy-load crash of
# #     # accessing member.user.full_name directly on an async session.

# #     user = await UserRepository(db).get_by_id(member.user_id)
# #     full_name = user.full_name if user else "Unknown User"

# #     return TeamMemberRead(
# #         id=member.id,
# #         user_id=member.user_id,
# #         user_full_name=full_name,
# #         role=member.role.value,
# #     )


# # @router.get("/{team_id}/members", response_model=list[TeamMemberRead])
# # async def list_team_members(
# #     organization_id: uuid.UUID,
# #     team_id: uuid.UUID,
# #     db: Annotated[AsyncSession, Depends(get_db)],
# # ) -> list[TeamMemberRead]:
# #     service = TeamService(db)
# #     members_with_names = await service.list_members_with_names(team_id)
# #     return [
# #         TeamMemberRead(
# #             id=m.id, user_id=m.user_id, user_full_name=name, role=m.role.value
# #         )
# #         for m, name in members_with_names
# #     ]


# import uuid
# from typing import Annotated

# from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.api.dependencies import get_current_user, require_permission
# from app.core.exceptions import (
#     TeamNotFoundError,
#     UserAlreadyTeamMemberError,
#     UserNotFoundError,
# )
# from app.db.session import get_db
# from app.enums.permissions import Permissions
# from app.models.user import User
# from app.repositories.user_repository import UserRepository
# from app.schemas.team import (
#     AddTeamMemberRequest,
#     InviteResponse,
#     TeamCreate,
#     TeamMemberRead,
#     TeamRead,
#     TeamUpdate,
# )
# from app.services.team_service import TeamService

# router = APIRouter(prefix="/organizations/{organization_id}/teams", tags=["teams"])


# @router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
# async def create_team(
#     organization_id: uuid.UUID,
#     payload: TeamCreate,
#     db: Annotated[AsyncSession, Depends(get_db)],
#     _: Annotated[None, Depends(require_permission(Permissions.TEAM_CREATE))],
# ) -> TeamRead:
#     service = TeamService(db)
#     team = await service.create_team(organization_id=organization_id, name=payload.name)
#     return TeamRead.model_validate(team)


# @router.get("", response_model=list[TeamRead])
# async def list_teams(
#     organization_id: uuid.UUID,
#     db: Annotated[AsyncSession, Depends(get_db)],
# ) -> list[TeamRead]:
#     service = TeamService(db)
#     teams = await service.list_teams(organization_id)
#     return [TeamRead.model_validate(t) for t in teams]


# @router.get("/{team_id}", response_model=TeamRead)
# async def get_team(
#     organization_id: uuid.UUID,
#     team_id: uuid.UUID,
#     db: Annotated[AsyncSession, Depends(get_db)],
# ) -> TeamRead:
#     service = TeamService(db)
#     team = await service.get_team(team_id)
#     return TeamRead.model_validate(team)


# @router.patch("/{team_id}", response_model=TeamRead)
# async def update_team(
#     organization_id: uuid.UUID,
#     team_id: uuid.UUID,
#     payload: TeamUpdate,
#     db: Annotated[AsyncSession, Depends(get_db)],
#     _: Annotated[None, Depends(require_permission(Permissions.TEAM_MANAGE_MEMBERS))],
# ) -> TeamRead:
#     service = TeamService(db)
#     team = await service.update_team(team_id=team_id, name=payload.name)
#     return TeamRead.model_validate(team)


# @router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_team(
#     organization_id: uuid.UUID,
#     team_id: uuid.UUID,
#     db: Annotated[AsyncSession, Depends(get_db)],
#     _: Annotated[None, Depends(require_permission(Permissions.TEAM_DELETE))],
# ) -> None:
#     service = TeamService(db)
#     await service.delete_team(team_id)


# @router.post(
#     "/{team_id}/invite",
#     response_model=InviteResponse,
#     status_code=status.HTTP_200_OK,
# )
# async def invite_team_member(
#     organization_id: uuid.UUID,
#     team_id: uuid.UUID,
#     payload: AddTeamMemberRequest,
#     background_tasks: BackgroundTasks,
#     current_user: Annotated[User, Depends(get_current_user)],
#     db: Annotated[AsyncSession, Depends(get_db)],
#     _: Annotated[None, Depends(require_permission(Permissions.TEAM_MANAGE_MEMBERS))],
# ) -> InviteResponse:
#     service = TeamService(db)
#     try:
#         await service.send_team_invitation(
#             organization_id=organization_id,
#             team_id=team_id,
#             email=payload.email,
#             role=payload.role,
#             inviter=current_user,
#             background_tasks=background_tasks,
#         )
#     except TeamNotFoundError as e:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

#     return InviteResponse(message=f"Invitation sent successfully to {payload.email}.")


# @router.post(
#     "/{team_id}/members",
#     response_model=TeamMemberRead,
#     status_code=status.HTTP_201_CREATED,
# )
# async def add_team_member(
#     organization_id: uuid.UUID,
#     team_id: uuid.UUID,
#     payload: AddTeamMemberRequest,
#     current_user: Annotated[User, Depends(get_current_user)],
#     db: Annotated[AsyncSession, Depends(get_db)],
#     _: Annotated[None, Depends(require_permission(Permissions.TEAM_MANAGE_MEMBERS))],
# ) -> TeamMemberRead:
#     service = TeamService(db)
#     try:
#         member = await service.send_team_invitation(
#             organization_id=organization_id,
#             team_id=team_id,
#             email=payload.email,
#             role=payload.role,
#         )
#     except TeamNotFoundError as e:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
#     except UserNotFoundError as e:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
#     except UserAlreadyTeamMemberError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
#         ) from e

#     user = await UserRepository(db).get_by_id(member.user_id)
#     full_name = user.full_name if user else "Unknown User"

#     return TeamMemberRead(
#         id=member.id,
#         user_id=member.user_id,
#         user_full_name=full_name,
#         role=member.role.value,
#     )


# @router.get("/{team_id}/members", response_model=list[TeamMemberRead])
# async def list_team_members(
#     organization_id: uuid.UUID,
#     team_id: uuid.UUID,
#     db: Annotated[AsyncSession, Depends(get_db)],
# ) -> list[TeamMemberRead]:
#     service = TeamService(db)
#     members_with_names = await service.list_members_with_names(team_id)
#     return [
#         TeamMemberRead(
#             id=m.id, user_id=m.user_id, user_full_name=name, role=m.role.value
#         )
#         for m, name in members_with_names
#     ]


import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_permission
from app.core.exceptions import (
    TeamNotFoundError,
    UserAlreadyTeamMemberError,
    UserNotFoundError,
    UserDeactivatedError,
)
from app.db.session import get_db
from app.enums.permissions import Permissions
from app.models.user import User
from app.schemas.team import (
    AddTeamMemberRequest,
    TeamCreate,
    TeamMemberRead,
    TeamRead,
    TeamUpdate,
)
from app.services.team_service import TeamService

router = APIRouter(prefix="/organizations/{organization_id}/teams", tags=["teams"])


@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team(
    organization_id: uuid.UUID,
    payload: TeamCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.TEAM_CREATE))],
) -> TeamRead:
    service = TeamService(db)
    team = await service.create_team(organization_id=organization_id, name=payload.name)
    return TeamRead.model_validate(team)


@router.get("", response_model=list[TeamRead])
async def list_teams(
    organization_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[TeamRead]:
    service = TeamService(db)
    teams = await service.list_teams(organization_id)
    return [TeamRead.model_validate(t) for t in teams]


@router.get("/{team_id}", response_model=TeamRead)
async def get_team(
    organization_id: uuid.UUID,
    team_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TeamRead:
    service = TeamService(db)
    team = await service.get_team(team_id)
    return TeamRead.model_validate(team)


@router.patch("/{team_id}", response_model=TeamRead)
async def update_team(
    organization_id: uuid.UUID,
    team_id: uuid.UUID,
    payload: TeamUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.TEAM_MANAGE_MEMBERS))],
) -> TeamRead:
    service = TeamService(db)
    team = await service.update_team(team_id=team_id, name=payload.name)
    return TeamRead.model_validate(team)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    organization_id: uuid.UUID,
    team_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.TEAM_DELETE))],
) -> None:
    service = TeamService(db)
    await service.delete_team(team_id)


@router.post("/{team_id}/invite", status_code=status.HTTP_200_OK)
async def invite_team_member(
    organization_id: uuid.UUID,
    team_id: uuid.UUID,
    payload: AddTeamMemberRequest,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.TEAM_MANAGE_MEMBERS))],
) -> dict:
    service = TeamService(db)
    clean_email = payload.email.strip().lower()
    try:
        return await service.send_team_invitation(
            organization_id=organization_id,
            team_id=team_id,
            email=clean_email,
            role=payload.role,
            inviter=current_user,
            background_tasks=background_tasks,
        )
    except (
        UserAlreadyTeamMemberError,
        UserNotFoundError,
        UserDeactivatedError,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except TeamNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/{team_id}/members", response_model=list[TeamMemberRead])
async def list_team_members(
    organization_id: uuid.UUID,
    team_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[TeamMemberRead]:
    service = TeamService(db)
    members_with_names = await service.list_members_with_names(team_id)
    return [
        TeamMemberRead(
            id=m.id, user_id=m.user_id, user_full_name=name, role=m.role.value
        )
        for m, name in members_with_names
    ]


@router.delete(
    "/{team_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_team_member(
    organization_id: uuid.UUID,
    team_id: uuid.UUID,
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    service = TeamService(session)
    await service.remove_member(team_id=team_id, user_id=user_id)
