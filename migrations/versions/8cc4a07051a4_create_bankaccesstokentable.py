"""create-bankaccesstokentable

Revision ID: 8cc4a07051a4
Revises: 2ed45ebea379
Create Date: 2021-05-21 23:19:19.531950

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8cc4a07051a4'
down_revision = '2ed45ebea379'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('bank_access_tokens',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('bank_name', sa.String),
                    sa.Column('access_token', sa.String))


def downgrade():
    op.drop_table('bank_access_tokens')
