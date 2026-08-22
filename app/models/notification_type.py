# app/models/notification_type.py
"""
NotificationType — lookup table replacing what would otherwise be a
native Postgres ENUM. Seeded via migration/seed script. See our earlier
design discussion: enums are cheap to query but painful to alter, and
notification types are the most likely to grow (AI features, new
integrations), so a lookup table trades a tiny join for zero-downtime
extensibility.
"""

import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from notification import Notification
from app.db.base import Base


class NotificationType(Base):
    __tablename__ = "notification_types"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    notifications: Mapped[list["Notification"]] = relationship(back_populates="type")

    def __repr__(self) -> str:
        return f"<NotificationType code={self.code!r}>"
