"""Make name of role and permission unique

Revision ID: 001fbf42cf28
Revises: 4b3a7d54ccf1
Create Date: 2025-03-27 14:06:57.532578

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001fbf42cf28'
down_revision: Union[str, None] = '4b3a7d54ccf1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'permissions', ['name'])
    op.create_unique_constraint(None, 'roles', ['name'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'roles', type_='unique')
    op.drop_constraint(None, 'permissions', type_='unique')
    # ### end Alembic commands ###
