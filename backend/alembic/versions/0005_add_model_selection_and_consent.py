from alembic import op
import sqlalchemy as sa

revision = "0005_add_model_selection_and_consent"
down_revision = "0004_harden_analysis_schema"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "analyses",
        sa.Column(
            "model_provider",
            sa.String(),
            nullable=False,
            server_default="PRODUCTION",
        ),
    )

    op.add_column(
        "analyses",
        sa.Column(
            "training_consent",
            sa.Boolean(),
            nullable=True,
        ),
    )

    op.add_column(
        "analyses",
        sa.Column(
            "training_status",
            sa.String(),
            nullable=False,
            server_default="NOT_REQUESTED",
        ),
    )


def downgrade():
    op.drop_column("analyses", "training_status")
    op.drop_column("analyses", "training_consent")
    op.drop_column("analyses", "model_provider")
