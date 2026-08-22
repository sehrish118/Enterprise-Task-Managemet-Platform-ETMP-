# app/models/user.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.organization_member import OrganizationMember
    from app.models.team_member import TeamMember
    from app.models.project import Project
    from app.models.project_member import ProjectMember
    from app.models.task import Task
    from app.models.task_assignee import TaskAssignee
    from app.models.comment import Comment
    from app.models.attachment import Attachment
    from app.models.notification import Notification
    from app.models.activity_log import ActivityLog
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import CITEXT
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    # CITEXT gives case-insensitive uniqueness at the DB level — no
    # separate LOWER(email) index needed. Requires the citext extension
    # (enabled in the first Alembic migration).
    email: Mapped[str] = mapped_column(CITEXT, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    organization_memberships: Mapped[list["OrganizationMember"]] = relationship(
        back_populates="user"
    )
    team_memberships: Mapped[list["TeamMember"]] = relationship(back_populates="user")
    created_projects: Mapped[list["Project"]] = relationship(back_populates="creator")
    project_memberships: Mapped[list["ProjectMember"]] = relationship(
        back_populates="user"
    )
    created_tasks: Mapped[list["Task"]] = relationship(back_populates="creator")
    task_assignments: Mapped[list["TaskAssignee"]] = relationship(back_populates="user")
    comments: Mapped[list["Comment"]] = relationship(back_populates="user")
    attachments: Mapped[list["Attachment"]] = relationship(back_populates="uploader")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")
    activity_logs: Mapped[list["ActivityLog"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
