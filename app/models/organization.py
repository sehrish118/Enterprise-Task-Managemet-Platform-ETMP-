import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
     from role import Role
     from organization_member import OrganizationMember
     from team import Team
     from project import Project
     from task_status import TaskStatus
     from activity_log import ActivityLog
     from notification import Notification
from app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
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

    roles: Mapped[list["Role"]] = relationship(back_populates="organization")
    members: Mapped[list["OrganizationMember"]] = relationship(
        back_populates="organization"
    )
    teams: Mapped[list["Team"]] = relationship(back_populates="organization")
    projects: Mapped[list["Project"]] = relationship(back_populates="organization")
    task_statuses: Mapped[list["TaskStatus"]] = relationship(
        back_populates="organization"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="organization"
    )
    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        back_populates="organization"
    )

    def __repr__(self) -> str:
        return f"<Organization id={self.id} slug={self.slug!r}>"
