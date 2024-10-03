"""Make send_alert column non-nullable with default value

Revision ID: 0f393e752bb0
Revises: 90c6535927e9
Create Date: 2024-10-03 14:12:21.571926

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f393e752bb0'
down_revision: Union[str, None] = '90c6535927e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Set the default value first for existing rows
    op.execute("UPDATE favorite_locations SET send_alert = false WHERE send_alert IS NULL")

    # Make the column non-nullable
    op.alter_column(
        'favorite_locations',
        'send_alert',
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.text('false')  # Optionally set a server default for new rows
    )


def downgrade() -> None:
    # Revert the column to be nullable again
    op.alter_column(
        'favorite_locations',
        'send_alert',
        existing_type=sa.Boolean(),
        nullable=True,
        server_default=None
    )
