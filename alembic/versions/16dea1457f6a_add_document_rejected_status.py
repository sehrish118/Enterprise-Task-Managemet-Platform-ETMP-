"""add_document_rejected_status

Revision ID: 16dea1457f6a
Revises: 1af2f03140e8
Create Date: 2026-08-30 01:03:53.762958

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "16dea1457f6a"
down_revision: Union[str, Sequence[str], None] = "1af2f03140e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "documents", sa.Column("rejection_reason", sa.String(length=255), nullable=True)
    )

    # Postgres requires new enum values to be committed before they can be
    # used in the same transaction elsewhere — autogenerate never detects
    # this, so it's added manually.
    op.execute("ALTER TYPE document_status ADD VALUE IF NOT EXISTS 'REJECTED'")


def downgrade() -> None:
    """Downgrade schema."""
    # Note: Postgres does not support removing a value from an enum type
    # directly. A full downgrade would require recreating the enum type
    # without 'REJECTED' and migrating the column over — omitted here as
    # it's rarely needed in practice for a dev/staging rollback.
    op.drop_column("documents", "rejection_reason")
