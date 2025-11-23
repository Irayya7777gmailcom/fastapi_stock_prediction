"""Initial migration - Create stock data tables

Revision ID: 001
Revises: 
Create Date: 2025-11-23 18:00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables"""
    
    # Create historical_data table
    op.create_table(
        'historical_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('stock', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('strike', sa.String(length=50), nullable=True),
        sa.Column('prev_oi', sa.String(length=50), nullable=True),
        sa.Column('latest_oi', sa.String(length=50), nullable=True),
        sa.Column('call_oi_difference', sa.String(length=50), nullable=True),
        sa.Column('put_oi_difference', sa.String(length=50), nullable=True),
        sa.Column('ltp', sa.String(length=50), nullable=True),
        sa.Column('additional_strike', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_historical_stock', 'historical_data', ['stock'])
    
    # Create live_data table
    op.create_table(
        'live_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('stock', sa.String(length=50), nullable=False),
        sa.Column('section', sa.String(length=100), nullable=True),
        sa.Column('label', sa.String(length=100), nullable=True),
        sa.Column('prev_oi', sa.String(length=50), nullable=True),
        sa.Column('strike', sa.String(length=50), nullable=True),
        sa.Column('oi_diff', sa.String(length=50), nullable=True),
        sa.Column('is_new_strike', sa.String(length=10), nullable=True),
        sa.Column('add_strike', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_live_stock', 'live_data', ['stock'])
    
    # Create processing_metadata table
    op.create_table(
        'processing_metadata',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('process_type', sa.String(length=50), nullable=False),
        sa.Column('stocks_processed', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create uploaded_files table
    op.create_table(
        'uploaded_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Drop all tables"""
    op.drop_table('uploaded_files')
    op.drop_table('processing_metadata')
    op.drop_index('idx_live_stock', table_name='live_data')
    op.drop_table('live_data')
    op.drop_index('idx_historical_stock', table_name='historical_data')
    op.drop_table('historical_data')
