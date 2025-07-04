"""add pending_case table"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'pending_case',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('folder_name', sa.String(length=128), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
    )
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.alter_column('case', 'restoration_items', type_=postgresql.JSONB())
        op.alter_column('case', 'shade_material', type_=postgresql.JSONB())


def downgrade():
    op.drop_table('pending_case')
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.alter_column('case', 'restoration_items', type_=sa.JSON())
        op.alter_column('case', 'shade_material', type_=sa.JSON())
