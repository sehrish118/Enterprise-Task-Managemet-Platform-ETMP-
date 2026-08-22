"""make team name uniqueness partial (exclude soft-deleted)

Revision ID: 258376d173df
Revises: 9b15d6842ceb
Create Date: 2026-07-29 11:24:20.253896

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "258376d173df"
down_revision: Union[str, Sequence[str], None] = "9b15d6842ceb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("uq_team_org_name", "teams", type_="unique")
    op.create_index(
        "uq_team_org_name",
        "teams",
        ["organization_id", "name"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("uq_team_org_name", table_name="teams")
    op.create_unique_constraint(
        "uq_team_org_name", "teams", ["organization_id", "name"]
    )
