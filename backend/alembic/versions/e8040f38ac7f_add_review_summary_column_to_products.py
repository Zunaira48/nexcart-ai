"""add review_summary column to products

Revision ID: e8040f38ac7f
Revises: 2720307df362
Create Date: 2026-08-12 03:18:17.469852

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8040f38ac7f'
down_revision: Union[str, Sequence[str], None] = '2720307df362'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('products', sa.Column('review_summary', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('products', 'review_summary')