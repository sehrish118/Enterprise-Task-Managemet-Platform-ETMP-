import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
     from role_permission import RolePermission
from app.db.base import Base


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(
        String(150), unique=True, nullable=False, index=True
    )
    role_links: Mapped[list["RolePermission"]] = relationship(
        back_populates="permission"
    )

    def __repr__(self) -> str:
        return f"<Permission id={self.id} name={self.name!r}>"
