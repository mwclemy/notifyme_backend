"""add-name-touser

Revision ID: c5e969715d10
Revises: 1d8aa7b318a6
Create Date: 2021-05-24 11:40:40.799238

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5e969715d10'
down_revision = '1d8aa7b318a6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users',
                  sa.Column('name', sa.String))


def downgrade():
    op.remove_column('users', 'name')
