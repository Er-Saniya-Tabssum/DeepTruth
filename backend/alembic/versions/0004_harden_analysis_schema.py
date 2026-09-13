from alembic import op
import sqlalchemy as sa

revision = "0004_harden_analysis_schema"
down_revision = "0003_create_removal_jobs"
branch_labels = None
depends_on = None


def upgrade():
    # Helpful indexes for dashboard/history/worker queries.
    op.create_index("ix_analyses_status_created_at", "analyses", ["status", "created_at"])
    op.create_index("ix_analyses_owner_created_at", "analyses", ["owner_id", "created_at"])
    op.create_index("ix_revoked_tokens_jti_lookup", "revoked_tokens", ["jti"])
    op.create_index("ix_removal_jobs_owner_created_at", "removal_jobs", ["owner_id", "created_at"])


def downgrade():
    op.drop_index("ix_removal_jobs_owner_created_at", table_name="removal_jobs")
    op.drop_index("ix_revoked_tokens_jti_lookup", table_name="revoked_tokens")
    op.drop_index("ix_analyses_owner_created_at", table_name="analyses")
    op.drop_index("ix_analyses_status_created_at", table_name="analyses")
