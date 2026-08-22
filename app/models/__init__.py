"""
Central model registry.

Importing every model here ensures they all register on Base.metadata
as soon as `app.models` is imported anywhere (e.g. from alembic/env.py).
Without this, SQLAlchemy has no way of knowing a model exists just
because its file exists — it needs to actually be imported once.
"""

from app.models.organization import Organization
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User
from app.models.organization_member import OrganizationMember
from app.models.team import Team
from app.models.team_member import TeamMember
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.task_status import TaskStatus
from app.models.task import Task
from app.models.task_assignee import TaskAssignee
from app.models.comment import Comment
from app.models.attachment import Attachment
from app.models.notification_type import NotificationType
from app.models.notification import Notification
from app.models.activity_log import ActivityLog

__all__ = [
    "Organization",
    "Permission",
    "Role",
    "RolePermission",
    "User",
    "OrganizationMember",
    "Team",
    "TeamMember",
    "Project",
    "ProjectMember",
    "TaskStatus",
    "Task",
    "TaskAssignee",
    "Comment",
    "Attachment",
    "NotificationType",
    "Notification",
    "ActivityLog",
]
