# app/db/seed.py


import asyncio

from sqlalchemy import select

from app.core.logging import get_logger
from app.db.session import async_session_local
from app.enums.permissions import Permissions
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.notification_type import NotificationType

logger = get_logger(__name__)

ROLE_PERMISSION_MAP = {
    "Owner": Permissions.all_permissions(),  # everything
    "Admin": [p for p in Permissions.all_permissions() if p != Permissions.ORG_DELETE],
    "Member": [
        Permissions.PROJECT_CREATE,
        Permissions.PROJECT_MANAGE_MEMBERS,
        Permissions.TASK_CREATE,
        Permissions.TASK_UPDATE,
        Permissions.TASK_ASSIGN,
    ],
}


async def seed_permissions(session) -> dict[str, Permission]:
    result = await session.execute(select(Permission))
    existing = {p.name: p for p in result.scalars().all()}

    for code in Permissions.all_permissions():
        if code not in existing:
            perm = Permission(name=code)
            session.add(perm)
            existing[code] = perm
            logger.info("Seeding permission", extra={"permission": code})

    await session.flush()
    return existing


async def seed_system_roles(
    session, permissions_by_name: dict[str, Permission]
) -> None:
    result = await session.execute(
        select(Role).where(
            Role.is_system_role.is_(True), Role.organization_id.is_(None)
        )
    )
    existing_roles = {r.name: r for r in result.scalars().all()}

    for role_name, permission_codes in ROLE_PERMISSION_MAP.items():
        role = existing_roles.get(role_name)
        if role is None:
            role = Role(name=role_name, is_system_role=True, organization_id=None)
            session.add(role)
            await session.flush()  # assigns role.id
            logger.info("Seeding system role", extra={"role": role_name})
            existing_roles[role_name] = role

        # Fetch already-mapped permission IDs for this role to avoid duplicates
        result = await session.execute(
            select(RolePermission.permission_id).where(
                RolePermission.role_id == role.id
            )
        )
        already_mapped = {row[0] for row in result.all()}

        for code in permission_codes:
            perm = permissions_by_name[code]
            if perm.id not in already_mapped:
                session.add(RolePermission(role_id=role.id, permission_id=perm.id))


NOTIFICATION_TYPES = {
    "TASK_ASSIGNED": "A task was assigned to you",
    "TASK_UPDATED": "A task you're involved in was updated",
    "TASK_COMPLETED": "A task was marked complete",
    "COMMENT_ADDED": "A new comment was added to a task",
    "MENTION": "You were mentioned in a comment",
    "PROJECT_INVITATION": "You were added to a project",
}


async def seed_notification_types(session) -> None:
    result = await session.execute(select(NotificationType))
    existing = {nt.code for nt in result.scalars().all()}

    for code, description in NOTIFICATION_TYPES.items():
        if code not in existing:
            session.add(NotificationType(code=code, description=description))
            logger.info("Seeding notification type", extra={"type": code})


async def run_seed() -> None:
    async with async_session_local() as session:
        permissions_by_name = await seed_permissions(session)
        await seed_system_roles(session, permissions_by_name)
        await seed_notification_types(session)
        await session.commit()
        logger.info("Seed complete.")


if __name__ == "__main__":
    asyncio.run(run_seed())
