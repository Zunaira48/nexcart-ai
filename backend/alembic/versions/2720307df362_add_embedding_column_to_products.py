"""add embedding column to products

Revision ID: 2720307df362
Revises: e16ab1a96cf1
Create Date: 2026-08-11 01:07:36.646556

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2720307df362'
down_revision: Union[str, Sequence[str], None] = 'e16ab1a96cf1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('products', sa.Column('embedding', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('products', 'embedding')