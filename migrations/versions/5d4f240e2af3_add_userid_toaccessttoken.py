"""add-userid-toaccessttoken

Revision ID: 5d4f240e2af3
Revises: c5e969715d10
Create Date: 2021-05-25 09:39:06.244136

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d4f240e2af3'
down_revision = 'c5e969715d10'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('bank_access_tokens',
                  sa.Column('user_id', sa.Integer))


def downgrade():
    op.remove_column('bank_access_tokens', 'user_id')
