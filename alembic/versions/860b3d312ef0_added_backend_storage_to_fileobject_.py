"""added backend_storage to FileObject table

Revision ID: 860b3d312ef0
Revises: 8634157233f5
Create Date: 2023-01-19 11:59:36.515101+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '860b3d312ef0'
down_revision = '8634157233f5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('file_object', sa.Column('backend_storage', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('file_object', 'backend_storage')
    # ### end Alembic commands ###