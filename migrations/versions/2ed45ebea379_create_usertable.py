"""create-usertable

Revision ID: 2ed45ebea379
Revises: 
Create Date: 2021-05-21 23:06:09.307577

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ed45ebea379'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('phone', sa.String, nullable=False, unique=True),
                    sa.Column('password', sa.String),
                    sa.Column('threshold_amount', sa.DECIMAL(10, 2)))


def downgrade():
    op.drop_table('users')
