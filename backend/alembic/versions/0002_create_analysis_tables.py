from alembic import op
import sqlalchemy as sa

revision = "0002_create_analysis_tables"
down_revision = "0001_create_auth"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "analyses",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("owner_id", sa.String(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("media_type", sa.String(), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("storage_path", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="QUEUED"),
        sa.Column("inference_mode", sa.String(), nullable=False, server_default="REAL"),
        sa.Column("progress", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("current_stage", sa.String(), nullable=True),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("error_code", sa.String(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_analyses_owner_id", "analyses", ["owner_id"])

    op.create_table(
        "detected_faces",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("analysis_id", sa.String(), sa.ForeignKey("analyses.id"), nullable=False),
        sa.Column("bbox_x", sa.Integer(), nullable=True),
        sa.Column("bbox_y", sa.Integer(), nullable=True),
        sa.Column("bbox_w", sa.Integer(), nullable=True),
        sa.Column("bbox_h", sa.Integer(), nullable=True),
        sa.Column("identity_name", sa.String(), nullable=True),
        sa.Column("identity_confidence", sa.Float(), nullable=True),
    )
    op.create_index("ix_detected_faces_analysis_id", "detected_faces", ["analysis_id"])

    op.create_table(
        "evidence",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("analysis_id", sa.String(), sa.ForeignKey("analyses.id"), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("size", sa.Integer(), nullable=True),
        sa.Column("media_type", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_evidence_analysis_id", "evidence", ["analysis_id"])

    op.create_table(
        "tracked_images",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("analysis_id", sa.String(), sa.ForeignKey("analyses.id"), nullable=True),
        sa.Column("source_url", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_tracked_images_analysis_id", "tracked_images", ["analysis_id"])

    op.create_table(
        "tracking_matches",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("tracked_image_id", sa.String(), sa.ForeignKey("tracked_images.id"), nullable=False),
        sa.Column("match_url", sa.String(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_tracking_matches_tracked_image_id", "tracking_matches", ["tracked_image_id"])

    op.create_table(
        "removal_requests",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("analysis_id", sa.String(), sa.ForeignKey("analyses.id"), nullable=True),
        sa.Column("target_url", sa.String(), nullable=False),
        sa.Column("platform", sa.String(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("contact_email", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="SUBMITTED"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table("removal_requests")
    op.drop_index("ix_tracking_matches_tracked_image_id", table_name="tracking_matches")
    op.drop_table("tracking_matches")
    op.drop_index("ix_tracked_images_analysis_id", table_name="tracked_images")
    op.drop_table("tracked_images")
    op.drop_index("ix_evidence_analysis_id", table_name="evidence")
    op.drop_table("evidence")
    op.drop_index("ix_detected_faces_analysis_id", table_name="detected_faces")
    op.drop_table("detected_faces")
    op.drop_index("ix_analyses_owner_id", table_name="analyses")
    op.drop_table("analyses")
