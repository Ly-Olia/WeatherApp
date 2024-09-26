"""Add auto_check_enabled field to User

Revision ID: 0072c8af6051
Revises: 9f753ee06805
Create Date: 2024-09-26 16:02:33.099070

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0072c8af6051'
down_revision: Union[str, None] = '9f753ee06805'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('auto_check_enabled', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('users', 'auto_check_enabled')
