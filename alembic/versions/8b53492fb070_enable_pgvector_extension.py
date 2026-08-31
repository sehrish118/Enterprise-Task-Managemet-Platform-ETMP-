# """enable_pgvector_extension

# Revision ID: 8b53492fb070
# Revises: 258376d173df
# Create Date: 2026-08-24 15:15:31.289584

# """
# from typing import Sequence, Union

# from alembic import op
# import sqlalchemy as sa


# # revision identifiers, used by Alembic.
# revision: str = '8b53492fb070'
# down_revision: Union[str, Sequence[str], None] = '258376d173df'
# branch_labels: Union[str, Sequence[str], None] = None
# depends_on: Union[str, Sequence[str], None] = None


# def upgrade() -> None:
#     """Upgrade schema."""
#     pass


# def downgrade() -> None:
#     """Downgrade schema."""
#     pass


"""enable_pgvector_extension

Revision ID: xxxxxxxxxxxx
Revises: <PASTE_YOUR_LATEST_REVISION_ID_HERE>
Create Date: 2026-08-24 ...
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "8b53492fb070"
down_revision = "258376d173df"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS vector;")
