"""Change colors to ARRAY type

Revision ID: eb61c4c11284
Revises: 00f6dd652f4b
Create Date: 2024-11-19 01:14:51.261208

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb61c4c11284'
down_revision: Union[str, None] = '00f6dd652f4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Alter 'colors' column from String to ARRAY(String)
    op.alter_column(
        'items',
        'colors',
        existing_type=sa.String(),
        type_=sa.ARRAY(sa.String()),
        existing_nullable=True
    )

def downgrade():
    # Revert 'colors' column back to String
    op.alter_column(
        'items',
        'colors',
        existing_type=sa.ARRAY(sa.String()),
        type_=sa.String(),
        existing_nullable=True
    )