"""empty message

Revision ID: a94bfa51c42e
Revises: 51dcd6bf4282
Create Date: 2020-07-29 20:16:30.130247

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a94bfa51c42e'
down_revision = '51dcd6bf4282'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('results', sa.Column('created', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('results', 'created')
    # ### end Alembic commands ###
