"""alterthresholdusercolumn

Revision ID: 1d8aa7b318a6
Revises: 8cc4a07051a4
Create Date: 2021-05-24 09:16:36.628154

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d8aa7b318a6'
down_revision = '8cc4a07051a4'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE users  alter column threshold_amount set default 100')


def downgrade():
    op.execute('ALTER TABLE users  alter column threshold_amount drop default')
