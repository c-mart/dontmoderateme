"""empty message

Revision ID: fdeac20e12c0
Revises: None
Create Date: 2016-05-01 07:24:46.062752

"""

# revision identifiers, used by Alembic.
revision = 'fdeac20e12c0'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_admin', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'is_admin')
    ### end Alembic commands ###
