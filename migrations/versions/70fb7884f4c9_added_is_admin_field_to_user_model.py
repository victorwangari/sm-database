"""Added is_admin field to User model

Revision ID: 70fb7884f4c9
Revises: <previous_revision_id>
Create Date: 2025-03-26 17:22:39.374135

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70fb7884f4c9'
down_revision = '<previous_revision_id>'  # Replace with actual previous revision ID
branch_labels = None
depends_on = None


def upgrade():
    # Add the is_admin column to the user table
    op.add_column('user', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.text('false')))


def downgrade():
    # Remove the is_admin column if rolling back
    op.drop_column('user', 'is_admin')
