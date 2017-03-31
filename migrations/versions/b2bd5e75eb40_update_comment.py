"""update Comment

Revision ID: b2bd5e75eb40
Revises: abc1dbdc84b2
Create Date: 2017-03-31 00:51:06.824748

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2bd5e75eb40'
down_revision = 'abc1dbdc84b2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column('author_name', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('comments', 'author_name')
    # ### end Alembic commands ###
