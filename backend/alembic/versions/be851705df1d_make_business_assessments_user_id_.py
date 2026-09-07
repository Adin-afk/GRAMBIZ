"""make business_assessments.user_id nullable

Revision ID: be851705df1d
Revises: 0f853a4a6ae1
Create Date: 2026-08-29 12:38:17.820924

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'be851705df1d'
down_revision: Union[str, None] = '0f853a4a6ae1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Allows anonymous/demo assessment creation without requiring login;
    # authenticated users still get user_id populated (see app/api/assessment.py).
    op.alter_column('business_assessments', 'user_id',
               existing_type=sa.UUID(),
               nullable=True)


def downgrade() -> None:
    op.alter_column('business_assessments', 'user_id',
               existing_type=sa.UUID(),
               nullable=False)
