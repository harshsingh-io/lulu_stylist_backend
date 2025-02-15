"""Update Tag and Item models to use tag names

Revision ID: a9b5fa664376
Revises: 54066ba1759f
Create Date: 2024-11-19 01:00:53.882092

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a9b5fa664376'
down_revision: Union[str, None] = '54066ba1759f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('item_tags', 'item_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('item_tags', 'tag_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.add_column('items', sa.Column('description', sa.String(), nullable=True))
    op.alter_column('items', 'user_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('items', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('items', 'category',
               existing_type=postgresql.ENUM('TOP', 'BOTTOM', 'SHOES', 'ACCESSORIES', 'INNERWEAR', 'OTHER', name='categoryenum'),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('items', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.String(),
               existing_nullable=True,
               existing_server_default=sa.text('now()'))
    op.alter_column('tags', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_index('ix_tags_name', table_name='tags')
    op.create_unique_constraint(None, 'tags', ['name'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tags', type_='unique')
    op.create_index('ix_tags_name', 'tags', ['name'], unique=True)
    op.alter_column('tags', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('items', 'created_at',
               existing_type=sa.String(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True,
               existing_server_default=sa.text('now()'))
    op.alter_column('items', 'category',
               existing_type=sa.String(),
               type_=postgresql.ENUM('TOP', 'BOTTOM', 'SHOES', 'ACCESSORIES', 'INNERWEAR', 'OTHER', name='categoryenum'),
               existing_nullable=True)
    op.alter_column('items', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('items', 'user_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.drop_column('items', 'description')
    op.alter_column('item_tags', 'tag_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.alter_column('item_tags', 'item_id',
               existing_type=sa.UUID(),
               nullable=True)
    # ### end Alembic commands ###
