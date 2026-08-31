"""add_document_embeddings_table

Revision ID: cfbc7085a875
Revises: 8b53492fb070
Create Date: 2026-08-24 15:26:13.794063

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy


# revision identifiers, used by Alembic.
revision: str = "cfbc7085a875"
down_revision: Union[str, Sequence[str], None] = "8b53492fb070"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "document_embeddings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=True),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.UUID(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "embedding", pgvector.sqlalchemy.vector.VECTOR(dim=384), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_document_embeddings_entity_id"),
        "document_embeddings",
        ["entity_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_embeddings_entity_type"),
        "document_embeddings",
        ["entity_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_embeddings_organization_id"),
        "document_embeddings",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_embeddings_project_id"),
        "document_embeddings",
        ["project_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_document_embeddings_project_id"), table_name="document_embeddings"
    )
    op.drop_index(
        op.f("ix_document_embeddings_organization_id"), table_name="document_embeddings"
    )
    op.drop_index(
        op.f("ix_document_embeddings_entity_type"), table_name="document_embeddings"
    )
    op.drop_index(
        op.f("ix_document_embeddings_entity_id"), table_name="document_embeddings"
    )
    op.drop_table("document_embeddings")
