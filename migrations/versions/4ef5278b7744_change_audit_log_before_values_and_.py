"""Change Audit log before_values and after_values data type JSON 

Revision ID: 4ef5278b7744
Revises: 2339f82b7661
Create Date: 2025-03-29 18:22:24.713292

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ef5278b7744'
down_revision: Union[str, None] = '2339f82b7661'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Cast the text columns to json explicitly using postgresql_using
    op.alter_column(
        'audit_logs', 
        'before_values',
        existing_type=sa.TEXT(),
        type_=sa.JSON(),
        existing_nullable=True,
        postgresql_using='before_values::json'
    )
    op.alter_column(
        'audit_logs', 
        'after_values',
        existing_type=sa.TEXT(),
        type_=sa.JSON(),
        existing_nullable=True,
        postgresql_using='after_values::json'
    )

def downgrade() -> None:
    """Downgrade schema."""
    # Cast JSON back to text (ensure that this cast meets your requirements for downgrade)
    op.alter_column(
        'audit_logs', 
        'after_values',
        existing_type=sa.JSON(),
        type_=sa.TEXT(),
        existing_nullable=True,
        postgresql_using='after_values::text'
    )
    op.alter_column(
        'audit_logs', 
        'before_values',
        existing_type=sa.JSON(),
        type_=sa.TEXT(),
        existing_nullable=True,
        postgresql_using='before_values::text'
    )
