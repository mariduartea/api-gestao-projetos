"""remove todo table

Revision ID: cf83ffeb786f
Revises: bc0f9b924f5d
Create Date: 2025-07-03 20:43:51.951936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf83ffeb786f'
down_revision: Union[str, None] = 'bc0f9b924f5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table('todo')


def downgrade() -> None:
    """Downgrade schema."""
    pass
