"""add_refresh_tokens_table

Revision ID: d00870e1ab46
Revises: 53900df29b35
Create Date: 2024-11-24 12:20:47.979608

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = 'd00870e1ab46'
down_revision: Union[str, None] = '53900df29b35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




def upgrade() -> None:
    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('token_id', sa.String(), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes
    op.create_index(
        'ix_refresh_tokens_id',
        'refresh_tokens',
        ['id'],
    )
    op.create_index(
        'ix_refresh_tokens_token_id',
        'refresh_tokens',
        ['token_id'],
        unique=True
    )
    op.create_index(
        'ix_refresh_tokens_user_id',
        'refresh_tokens',
        ['user_id']
    )
    
    # Create composite index for token lookups
    op.create_index(
        'ix_refresh_tokens_lookup',
        'refresh_tokens',
        ['token_id', 'is_revoked', 'expires_at']
    )

def downgrade() -> None:
    # Drop indexes first
    op.drop_index('ix_refresh_tokens_lookup')
    op.drop_index('ix_refresh_tokens_user_id')
    op.drop_index('ix_refresh_tokens_token_id')
    op.drop_index('ix_refresh_tokens_id')
    
    # Drop the table
    op.drop_table('refresh_tokens')