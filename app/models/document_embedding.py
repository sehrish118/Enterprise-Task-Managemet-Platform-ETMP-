# app/models/document_embedding.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.project import Project

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Embedding dimension must match the SentenceTransformers model output.
# e.g. "all-MiniLM-L6-v2" -> 384 dims. If the embedding model changes later,
# this constant AND the column below must be updated together (requires a migration).
EMBEDDING_DIM = 384


class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Nullable: some embedded content (e.g. an org-level uploaded document)
    # may not belong to any single project.
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # "task" / "comment" / "uploaded_document" — what kind of source this
    # embedding chunk came from.
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # The source row's id (task.id, comment.id, or an uploaded_document id).
    # Not a hard FK since entity_type varies across multiple tables.
    entity_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(
        Vector(EMBEDDING_DIM), nullable=False
    )

    chunk_index: Mapped[int] = mapped_column(
        nullable=False, default=0, server_default="0"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    organization: Mapped["Organization"] = relationship()
    project: Mapped["Project | None"] = relationship()

    def __repr__(self) -> str:
        return (
            f"<DocumentEmbedding id={self.id} entity_type={self.entity_type!r} "
            f"entity_id={self.entity_id}>"
        )
