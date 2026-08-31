# app/rag/rbac_scope.py
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidCredentialsError
from app.repositories.rbac_repository import RBACRepository
from app.services.project_service import ProjectService


@dataclass
class ChatbotScope:
    organization_id: uuid.UUID
    user_id: uuid.UUID
    allowed_project_ids: list[uuid.UUID] | None
    is_admin_or_owner: bool


async def resolve_scope(
    session: AsyncSession, *, organization_id: uuid.UUID, user_id: uuid.UUID
) -> ChatbotScope:
    rbac_repo = RBACRepository(session)

    is_member = await rbac_repo.is_organization_member(
        user_id=user_id, organization_id=organization_id
    )
    if not is_member:
        raise InvalidCredentialsError(
            "You do not have access to this organization's assistant."
        )

    is_admin_or_owner = await rbac_repo.user_is_org_admin_or_owner(
        user_id=user_id, organization_id=organization_id
    )

    # Reuse ProjectService.list_projects() — the exact same method the
    # REST API uses — instead of re-deriving visibility rules here.
    visible_projects = await ProjectService(session).list_projects(
        organization_id=organization_id, requesting_user_id=user_id
    )

    return ChatbotScope(
        organization_id=organization_id,
        user_id=user_id,
        allowed_project_ids=None
        if is_admin_or_owner
        else [p.id for p in visible_projects],
        is_admin_or_owner=is_admin_or_owner,
    )
