"""Add item priority

Revision ID: a7b2c3d4e5f6
Revises: fe56fa70289e
"""

import sqlalchemy as sa
from alembic import op

revision = "a7b2c3d4e5f6"
down_revision = "fe56fa70289e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The server default also backfills existing items.
    op.add_column(
        "item",
        sa.Column(
            "priority", sa.String(length=6), nullable=False, server_default="medium"
        ),
    )
    op.create_check_constraint(
        "item_priority", "item", "priority IN ('low', 'medium', 'high')"
    )


def downgrade() -> None:
    op.drop_constraint("item_priority", "item", type_="check")
    op.drop_column("item", "priority")
