from alembic import op
import sqlalchemy as sa

revision = "0003_create_removal_jobs"
down_revision = "0002_create_analysis_tables"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "removal_jobs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("owner_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("mode", sa.String(), nullable=False),
        sa.Column("source_path", sa.String(), nullable=False),
        sa.Column("mask_path", sa.String(), nullable=True),
        sa.Column("output_path", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="QUEUED"),
        sa.Column("model_name", sa.String(), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("detected_regions", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_removal_jobs_owner_id", "removal_jobs", ["owner_id"])


def downgrade():
    op.drop_index("ix_removal_jobs_owner_id", table_name="removal_jobs")
    op.drop_table("removal_jobs")
