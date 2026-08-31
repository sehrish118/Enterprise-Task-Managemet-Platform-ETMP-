# app/rag/tools.py
"""
Chatbot tools. Every function here is a thin wrapper around an existing
Service — permission/visibility logic is NEVER re-implemented here, it's
always delegated to the same Service the REST API already uses.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import TeamNotFoundError
from app.rag.rbac_scope import ChatbotScope
from app.repositories.rbac_repository import RBACRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.task_status_repository import TaskStatusRepository
from app.repositories.team_repository import TeamRepository
from app.services.dashboard_service import DashboardService
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.services.team_service import TeamService
from app.services.user_service import UserService


async def count_organization_members(
    session: AsyncSession, scope: ChatbotScope
) -> dict:
    if not scope.is_admin_or_owner:
        return {
            "error": (
                "I'm sorry, organization-wide member details are available "
                "to Admins and Owners only."
            )
        }
    members = await UserService(session).list_organization_users(
        organization_id=scope.organization_id
    )
    return {"member_count": len(members)}


async def list_organization_members(session: AsyncSession, scope: ChatbotScope) -> dict:
    if not scope.is_admin_or_owner:
        return {
            "error": (
                "I'm sorry, organization-wide member details are available "
                "to Admins and Owners only."
            )
        }
    members = await UserService(session).list_organization_users(
        organization_id=scope.organization_id
    )
    names = [u.full_name for u, *_rest in members]
    return {"member_count": len(names), "members": names}


async def list_team_members(
    session: AsyncSession, scope: ChatbotScope, *, team_name: str
) -> dict:
    team_repo = TeamRepository(session)
    team = await team_repo.get_by_name(
        organization_id=scope.organization_id, name=team_name
    )
    if team is None:
        return {"error": f"No team named '{team_name}' found in this organization."}

    try:
        members = await TeamService(session).list_members_with_names(team.id)
    except TeamNotFoundError:
        return {"error": f"No team named '{team_name}' found."}

    return {"team_name": team.name, "members": [name for _member, name in members]}


async def list_organization_teams(session: AsyncSession, scope: ChatbotScope) -> dict:
    # Per the RBAC matrix, viewing the team list is read-only and open
    # to every organization member — no admin/owner gate needed here.
    team_repo = TeamRepository(session)
    teams = await team_repo.list_by_organization(scope.organization_id)
    return {"team_count": len(teams), "teams": [t.name for t in teams]}


async def list_organization_projects(
    session: AsyncSession, scope: ChatbotScope
) -> dict:
    # ProjectService.list_projects() already applies the Owner/Admin
    # (see-all) vs Member (see-mine) rule internally.
    projects = await ProjectService(session).list_projects(
        organization_id=scope.organization_id, requesting_user_id=scope.user_id
    )
    return {"projects": [p.name for p in projects]}


async def list_project_tasks(
    session: AsyncSession, scope: ChatbotScope, *, project_name: str
) -> dict:
    from app.repositories.project_repository import ProjectRepository

    project_repo = ProjectRepository(session)
    project = await project_repo.get_by_name(
        organization_id=scope.organization_id, name=project_name
    )
    if project is None:
        return {"error": f"No project named '{project_name}' found."}

    # Visibility check delegated to the scope, which itself was built
    # from ProjectService.list_projects() — not re-derived here.
    if not scope.is_admin_or_owner:
        if (
            scope.allowed_project_ids is None
            or project.id not in scope.allowed_project_ids
        ):
            return {"error": f"You don't have access to project '{project_name}'."}

    task_service = TaskService(session)
    status_repo = TaskStatusRepository(session)

    tasks, _total = (
        await task_service.list_tasks(project.id, page_size=100)
        if False
        else await task_service.list_tasks(project.id)
    )

    status_cache: dict[uuid.UUID, str] = {}
    results = []
    for task in tasks:
        if task.status_id not in status_cache:
            status_obj = await status_repo.get_by_id(task.status_id)
            status_cache[task.status_id] = status_obj.name if status_obj else "Unknown"

        assignees = await task_service.list_assignees_with_names(task.id)
        results.append(
            {
                "title": task.title,
                "status": status_cache[task.status_id],
                "assignees": [name for _a, name in assignees],
            }
        )
    return {"project_name": project.name, "tasks": results}


async def count_user_teams(
    session: AsyncSession, scope: ChatbotScope, *, user_full_name: str
) -> dict:
    from app.repositories.user_repository import UserRepository

    user_repo = UserRepository(session)
    team_repo = TeamRepository(session)

    all_members = await UserService(session).list_organization_users(
        organization_id=scope.organization_id
    )
    target = next(
        (
            u
            for u, *_rest in all_members
            if u.full_name.lower() == user_full_name.lower()
        ),
        None,
    )
    if target is None:
        return {
            "error": f"No user named '{user_full_name}' found in this organization."
        }

    teams = await team_repo.list_teams_for_user(
        organization_id=scope.organization_id, user_id=target.id
    )
    return {
        "user": user_full_name,
        "team_count": len(teams),
        "teams": [t.name for t in teams],
    }


async def list_user_assigned_tasks(
    session: AsyncSession, scope: ChatbotScope, *, user_full_name: str
) -> dict:
    task_repo = TaskRepository(session)

    all_members = await UserService(session).list_organization_users(
        organization_id=scope.organization_id
    )

    # Exact match first
    exact_matches = [
        u for u, *_rest in all_members if u.full_name.lower() == user_full_name.lower()
    ]

    if len(exact_matches) == 1:
        target = exact_matches[0]
    elif len(exact_matches) == 0:
        # No exact match — check for partial matches to guide the user
        partial_matches = [
            u.full_name
            for u, *_rest in all_members
            if user_full_name.lower() in u.full_name.lower()
        ]
        if partial_matches:
            return {
                "error": (
                    f"No exact match for '{user_full_name}'. Did you mean one of: "
                    f"{', '.join(partial_matches)}? Please specify the full name."
                )
            }
        return {
            "error": f"No user named '{user_full_name}' found in this organization."
        }
    else:
        # Multiple exact matches (shouldn't normally happen, but be safe)
        return {
            "error": f"Multiple members named '{user_full_name}' found. Please provide more detail."
        }

    if not scope.is_admin_or_owner and target.id != scope.user_id:
        return {
            "error": "You can only view your own assigned tasks, not another member's."
        }

    tasks = await task_repo.list_assigned_to_user(
        organization_id=scope.organization_id, user_id=target.id
    )
    if not scope.is_admin_or_owner:
        allowed = set(scope.allowed_project_ids or [])
        tasks = [t for t in tasks if t.project_id in allowed]

    return {
        "user": target.full_name,
        "tasks": [{"title": t.title, "priority": t.priority.value} for t in tasks],
    }


async def get_organization_dashboard(
    session: AsyncSession, scope: ChatbotScope
) -> dict:
    # The route gates this behind an Owner/Admin permission dependency;
    # the service itself doesn't check, so we enforce it here the same
    # way the route would.
    if not scope.is_admin_or_owner:
        return {"error": "Only Owners and Admins can view the organization dashboard."}

    dashboard = await DashboardService(session).get_organization_dashboard(
        scope.organization_id
    )
    return {
        "total_projects": dashboard.total_projects,
        "active_projects": dashboard.active_projects,
        "total_tasks": dashboard.total_tasks,
        "total_members": dashboard.total_members,
        "tasks_by_priority": dashboard.tasks_by_priority,
    }


async def get_my_dashboard(session: AsyncSession, scope: ChatbotScope) -> dict:
    dashboard = await DashboardService(session).get_my_dashboard(scope.user_id)
    return {
        "assigned_tasks_count": dashboard.assigned_tasks_count,
        "overdue_tasks_count": dashboard.overdue_tasks_count,
        "unread_notifications_count": dashboard.unread_notifications_count,
        "recent_tasks": [t.title for t in dashboard.recent_tasks],
    }


# ── Tool schemas for the LLM ──────────────────────────────────────────
TOOL_SCHEMAS = [
    {
        "name": "count_organization_members",
        "description": "Get the total number of members in the current organization.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "list_organization_members",
        "description": "List the full names of all members in the current organization.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "list_team_members",
        "description": "List the members of a specific team by team name.",
        "input_schema": {
            "type": "object",
            "properties": {"team_name": {"type": "string"}},
            "required": ["team_name"],
        },
    },
    {
        "name": "list_organization_teams",
        "description": "List the names of all teams in the current organization.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "list_organization_projects",
        "description": "List projects in the organization visible to the current user.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "list_project_tasks",
        "description": "List tasks in a specific project, with their status and assignees, by project name.",
        "input_schema": {
            "type": "object",
            "properties": {"project_name": {"type": "string"}},
            "required": ["project_name"],
        },
    },
    {
        "name": "count_user_teams",
        "description": "Find out how many teams a specific person (by full name) is part of.",
        "input_schema": {
            "type": "object",
            "properties": {"user_full_name": {"type": "string"}},
            "required": ["user_full_name"],
        },
    },
    {
        "name": "list_user_assigned_tasks",
        "description": "List tasks assigned to a specific person (by full name), across all their projects.",
        "input_schema": {
            "type": "object",
            "properties": {"user_full_name": {"type": "string"}},
            "required": ["user_full_name"],
        },
    },
    {
        "name": "get_organization_dashboard",
        "description": "Get organization-wide stats: total projects, active projects, total tasks, total members, tasks by priority. Owner/Admin only.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_my_dashboard",
        "description": "Get the current user's own dashboard: their assigned tasks, overdue tasks, unread notifications.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]

TOOL_DISPATCH = {
    "count_organization_members": count_organization_members,
    "list_team_members": list_team_members,
    "list_organization_projects": list_organization_projects,
    "list_project_tasks": list_project_tasks,
    "count_user_teams": count_user_teams,
    "list_user_assigned_tasks": list_user_assigned_tasks,
    "get_organization_dashboard": get_organization_dashboard,
    "get_my_dashboard": get_my_dashboard,
    "list_organization_members": list_organization_members,
    "list_organization_teams": list_organization_teams,
}


async def execute_tool(
    session: AsyncSession, scope: ChatbotScope, *, tool_name: str, tool_input: dict
) -> dict:
    import inspect

    func = TOOL_DISPATCH.get(tool_name)
    if func is None:
        return {"error": f"Unknown tool: {tool_name}"}

    sig = inspect.signature(func)
    allowed_params = set(sig.parameters) - {"session", "scope"}
    filtered_input = {k: v for k, v in tool_input.items() if k in allowed_params}

    return await func(session, scope, **filtered_input)
