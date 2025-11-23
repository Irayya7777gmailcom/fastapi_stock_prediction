"""add_timestamps_to_processing_metadata

Revision ID: 5a431f748304
Revises: 001
Create Date: 2025-11-23 20:08:55.635259

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a431f748304'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add created_at and updated_at columns to processing_metadata table
    op.add_column('processing_metadata', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.add_column('processing_metadata', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))


def downgrade() -> None:
    # Remove created_at and updated_at columns
    op.drop_column('processing_metadata', 'updated_at')
    op.drop_column('processing_metadata', 'created_at')
