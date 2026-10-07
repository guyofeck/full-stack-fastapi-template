"""Add priority to Item

Revision ID: a1b2c3d4e5f6
Revises: fe56fa70289e
Create Date: 2026-10-07 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'fe56fa70289e'
branch_labels = None
depends_on = None


def upgrade():
    priority_enum = sa.Enum('low', 'medium', 'high', name='priority')
    priority_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'item',
        sa.Column('priority', priority_enum, nullable=False, server_default='medium'),
    )


def downgrade():
    op.drop_column('item', 'priority')
    sa.Enum(name='priority').drop(op.get_bind(), checkfirst=True)
