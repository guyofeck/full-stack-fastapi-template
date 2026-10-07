"""Add item priority

Revision ID: b7c4a21d9e03
Revises: fe56fa70289e
"""
from alembic import op
import sqlalchemy as sa

revision = "b7c4a21d9e03"
down_revision = "fe56fa70289e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "item",
        sa.Column("priority", sa.String(6), nullable=False, server_default="medium"),
    )
    op.create_check_constraint(
        "item_priority", "item", "priority IN ('low', 'medium', 'high')"
    )


def downgrade():
    op.drop_constraint("item_priority", "item", type_="check")
    op.drop_column("item", "priority")
