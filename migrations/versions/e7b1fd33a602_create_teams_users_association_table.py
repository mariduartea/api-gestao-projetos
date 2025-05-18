"""create teams_users association table

Revision ID: e7b1fd33a602
Revises: c0d8dde02839
Create Date: 2025-05-18 17:36:55.429098

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7b1fd33a602'
down_revision: Union[str, None] = 'c0d8dde02839'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'teams_users',
        sa.Column('team_id', sa.Integer, sa.ForeignKey('teams.id'), primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), primary_key=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('teams_users')
