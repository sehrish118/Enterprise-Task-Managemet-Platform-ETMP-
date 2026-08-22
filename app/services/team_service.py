# import uuid

# from sqlalchemy.ext.asyncio import AsyncSession

# from app.core.exceptions import (
#     TeamNameAlreadyExistsError,
#     TeamNotFoundError,
#     UserAlreadyTeamMemberError,
#     UserNotFoundError,
#     UserNotOrganizationMemberError,
# )
# from app.models.team import Team
# from app.models.team_member import TeamMember, TeamMemberRole
# from app.repositories.team_repository import TeamRepository
# from app.repositories.user_repository import UserRepository
# from app.repositories.organization_repository import OrganizationRepository
# from fastapi import BackgroundTasks
# from app.core.config import settings
# from app.core.security import create_invite_token
# from app.models.user import User
# from app.services.email_service import EmailService


# class TeamService:
#     def __init__(self, session: AsyncSession) -> None:
#         self.session = session
#         self.team_repo = TeamRepository(session)
#         self.user_repo = UserRepository(session)
#         self.org_repo = OrganizationRepository(session)

#     async def create_team(self, *, organization_id: uuid.UUID, name: str) -> Team:
#         existing = await self.team_repo.get_by_name(
#             organization_id=organization_id, name=name
#         )
#         if existing is not None:
#             raise TeamNameAlreadyExistsError(
#                 f"Team '{name}' already exists in this organization"
#             )
#         team = await self.team_repo.create(organization_id=organization_id, name=name)
#         await self.session.commit()
#         return team

#     async def get_team(self, team_id: uuid.UUID) -> Team:
#         team = await self.team_repo.get_by_id(team_id)
#         if team is None:
#             raise TeamNotFoundError(f"Team {team_id} not found")
#         return team

#     async def update_team(self, *, team_id: uuid.UUID, name: str | None) -> Team:
#         team = await self.get_team(team_id)
#         team = await self.team_repo.update(team, name=name)
#         await self.session.commit()
#         return team

#     async def delete_team(self, team_id: uuid.UUID) -> None:
#         team = await self.get_team(team_id)
#         await self.team_repo.soft_delete(team)
#         await self.session.commit()

#     async def list_teams(self, organization_id: uuid.UUID) -> list[Team]:
#         return await self.team_repo.list_by_organization(organization_id)

#     async def add_member(
#         self, *, organization_id: uuid.UUID, team_id: uuid.UUID, email: str, role: str
#     ) -> TeamMember:
#         await self.get_team(team_id)  # raises TeamNotFoundError if missing

#         user = await self.user_repo.get_by_email(email)
#         if user is None:
#             raise UserNotFoundError(f"No user registered with email '{email}'")

#         org_membership = await self.org_repo.get_membership(
#             organization_id=organization_id, user_id=user.id
#         )
#         if org_membership is None:
#             raise UserNotOrganizationMemberError(
#                 f"'{email}' must be a member of the organization before joining a team"
#             )

#         existing = await self.team_repo.get_membership(team_id=team_id, user_id=user.id)
#         if existing is not None:
#             raise UserAlreadyTeamMemberError(
#                 f"'{email}' is already a member of this team"
#             )

#         member = await self.team_repo.add_member(
#             organization_id=organization_id,
#             team_id=team_id,
#             user_id=user.id,
#             role=TeamMemberRole(role),
#         )
#         await self.session.commit()
#         return member


#     async def list_members(self, team_id: uuid.UUID) -> list[TeamMember]:
#         await self.get_team(team_id)
#         return await self.team_repo.list_members(team_id)

#     async def list_members_with_names(self, team_id: uuid.UUID) -> list[tuple]:
#         await self.get_team(team_id)
#         return await self.team_repo.list_members_with_names(team_id)

#     async def send_team_invitation(
#         self,
#         *,
#         organization_id: uuid.UUID,
#         team_id: uuid.UUID,
#         email: str,
#         role: str,
#         inviter: User,
#         background_tasks: BackgroundTasks,
#     ) -> None:
#         team = await self.team_repo.get_by_id(team_id)
#         if not team:
#             raise TeamNotFoundError(f"Team with ID {team_id} not found.")

#         token = create_invite_token(
#             email=email,
#             organization_id=organization_id,
#             team_id=team_id,
#             role=role,
#         )

#         invite_link = f"{settings.FRONTEND_URL}/accept-invite?token={token}"

#         background_tasks.add_task(
#             EmailService.send_team_invite,
#             to_email=email,
#             invite_link=invite_link,
#             team_name=team.name,
#             inviter_name=inviter.full_name or "An Organization Admin",
#         )

import uuid

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    TeamNameAlreadyExistsError,
    TeamNotFoundError,
    UserAlreadyTeamMemberError,
    UserDeactivatedError,
)
from app.core.security import create_invite_token
from app.models.team import Team
from app.models.team_member import TeamMember, TeamMemberRole
from app.models.user import User
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.team_repository import TeamRepository
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService


class TeamService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.team_repo = TeamRepository(session)
        self.user_repo = UserRepository(session)
        self.org_repo = OrganizationRepository(session)

    async def create_team(self, *, organization_id: uuid.UUID, name: str) -> Team:
        existing = await self.team_repo.get_by_name(
            organization_id=organization_id, name=name
        )
        if existing is not None:
            raise TeamNameAlreadyExistsError(
                f"Team '{name}' already exists in this organization"
            )
        team = await self.team_repo.create(organization_id=organization_id, name=name)
        await self.session.commit()
        return team

    async def get_team(self, team_id: uuid.UUID) -> Team:
        team = await self.team_repo.get_by_id(team_id)
        if team is None:
            raise TeamNotFoundError(f"Team {team_id} not found")
        return team

    async def update_team(self, *, team_id: uuid.UUID, name: str | None) -> Team:
        team = await self.get_team(team_id)
        team = await self.team_repo.update(team, name=name)
        await self.session.commit()
        return team

    async def delete_team(self, team_id: uuid.UUID) -> None:
        team = await self.get_team(team_id)
        await self.team_repo.soft_delete(team)
        await self.session.commit()

    async def list_teams(self, organization_id: uuid.UUID) -> list[Team]:
        return await self.team_repo.list_by_organization(organization_id)

    async def list_members(self, team_id: uuid.UUID) -> list[TeamMember]:
        await self.get_team(team_id)
        return await self.team_repo.list_members(team_id)

    async def list_members_with_names(self, team_id: uuid.UUID) -> list[tuple]:
        await self.get_team(team_id)
        return await self.team_repo.list_members_with_names(team_id)

    async def send_team_invitation(
        self,
        *,
        organization_id: uuid.UUID,
        team_id: uuid.UUID,
        email: str,
        role: str,
        inviter: User,
        background_tasks: BackgroundTasks,
    ) -> dict:
        team = await self.team_repo.get_by_id(team_id)
        if not team:
            raise TeamNotFoundError(f"Team with ID {team_id} not found.")

        # 1. Check if user already exists in DB
        user = await self.user_repo.get_by_email(email)

        if user:
            # Fetch Org Membership (Handles single object OR tuple return)
            membership_data = await self.org_repo.get_any_membership(
                organization_id=organization_id, user_id=user.id
            )

            if isinstance(membership_data, tuple):
                org_membership, user_obj = membership_data
            else:
                org_membership = membership_data
                user_obj = user

            if org_membership:
                # Check 1: Deactivated check (User.is_active is False OR deleted_at is NOT None)
                is_deactivated = (user_obj.is_active is False) or (
                    getattr(org_membership, "deleted_at", None) is not None
                )

                if is_deactivated:
                    raise UserDeactivatedError(
                        f"User '{email}' is currently deactivated. Please reactivate"
                        " them first."
                    )

                # Check 2: User is already in this team
                existing_team_member = await self.team_repo.get_membership(
                    team_id=team_id, user_id=user.id
                )
                if existing_team_member:
                    raise UserAlreadyTeamMemberError(
                        f"'{email}' is already a member of this team"
                    )

                # WORKFLOW B: User exists in Organization -> Direct Add to Team
                await self.team_repo.add_member(
                    organization_id=organization_id,
                    team_id=team_id,
                    user_id=user.id,
                    role=TeamMemberRole(role),
                )
                await self.session.commit()
                return {
                    "type": "DIRECT_ADD",
                    "message": f"User '{email}' was directly added to the team.",
                }

        # WORKFLOW A: User does NOT exist in Organization/DB -> Send Email Invite
        token = create_invite_token(
            email=email,
            organization_id=organization_id,
            team_id=team_id,
            role=role,
        )

        invite_link = f"{settings.FRONTEND_URL}/accept-invite?token={token}"

        background_tasks.add_task(
            EmailService.send_team_invite,
            to_email=email,
            invite_link=invite_link,
            team_name=team.name,
            inviter_name=inviter.full_name or "An Organization Admin",
        )

        return {
            "type": "EMAIL_INVITE",
            "message": f"Invitation email sent to '{email}'.",
        }

    async def remove_member(self, *, team_id: uuid.UUID, user_id: uuid.UUID) -> None:
        await self.get_team(team_id)  # Raises TeamNotFoundError if missing
        await self.team_repo.remove_member(team_id=team_id, user_id=user_id)
        await self.session.commit()
