from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_auth'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('role', sa.String(), nullable=False, server_default='USER'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'revoked_tokens',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('jti', sa.String(), nullable=False, index=True),
        sa.Column('revoked_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table('revoked_tokens')
    op.drop_table('users')
