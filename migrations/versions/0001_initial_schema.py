"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-04 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── teams ────────────────────────────────────────────────────
    op.create_table(
        "teams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── users ────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("username", sa.String(100), nullable=False, unique=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="viewer"),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("teams.id"), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_username", "users", ["username"])

    # ── api_keys ─────────────────────────────────────────────────
    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("key_hash", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── api_endpoints ────────────────────────────────────────────
    op.create_table(
        "api_endpoints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("base_url", sa.String(500), nullable=False),
        sa.Column("path", sa.String(500), nullable=False),
        sa.Column("method", sa.String(10), nullable=False, server_default="GET"),
        sa.Column("owner_team", sa.String(100), nullable=True),
        sa.Column("owner_email", sa.String(255), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("sla_latency_p99_ms", sa.Float(), nullable=True),
        sa.Column("sla_uptime_percent", sa.Float(), server_default="99.9"),
        sa.Column("sla_error_rate_max", sa.Float(), server_default="1.0"),
        sa.Column("is_public", sa.Boolean(), server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── api_versions ─────────────────────────────────────────────
    op.create_table(
        "api_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("api_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_endpoints.id"), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("changelog", sa.Text(), nullable=True),
        sa.Column("is_deprecated", sa.Boolean(), server_default=sa.false()),
        sa.Column("deprecated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── api_tags ─────────────────────────────────────────────────
    op.create_table(
        "api_tags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.Column("color", sa.String(7), server_default="#6366f1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── api_endpoint_tags (M2M) ──────────────────────────────────
    op.create_table(
        "api_endpoint_tags",
        sa.Column("api_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_endpoints.id"), primary_key=True),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_tags.id"), primary_key=True),
    )

    # ── request_logs ─────────────────────────────────────────────
    op.create_table(
        "request_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("api_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_endpoints.id"), nullable=False),
        sa.Column("endpoint_path", sa.String(500), nullable=False),
        sa.Column("method", sa.String(10), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column("request_size_bytes", sa.Integer(), nullable=True),
        sa.Column("response_size_bytes", sa.Integer(), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("client_ip", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("trace_id", sa.String(100), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("extra", postgresql.JSONB(), nullable=True),
    )
    op.create_index("ix_request_logs_api_id", "request_logs", ["api_id"])
    op.create_index("ix_request_logs_api_id_timestamp", "request_logs", ["api_id", "timestamp"])
    op.create_index("ix_request_logs_timestamp", "request_logs", ["timestamp"])

    # ── error_logs ───────────────────────────────────────────────
    op.create_table(
        "error_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("api_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_endpoints.id"), nullable=False),
        sa.Column("request_log_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("request_logs.id"), nullable=True),
        sa.Column("endpoint_path", sa.String(500), nullable=False),
        sa.Column("method", sa.String(10), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("error_type", sa.String(100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("stack_trace", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_error_logs_api_id", "error_logs", ["api_id"])
    op.create_index("ix_error_logs_api_id_timestamp", "error_logs", ["api_id", "timestamp"])

    # ── health_checks ────────────────────────────────────────────
    op.create_table(
        "health_checks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("api_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_endpoints.id"), nullable=False),
        sa.Column("is_healthy", sa.Boolean(), nullable=False),
        sa.Column("health_score", sa.Float(), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("uptime_percent", sa.Float(), nullable=True),
        sa.Column("error_rate_percent", sa.Float(), nullable=True),
        sa.Column("p99_latency_ms", sa.Float(), nullable=True),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("details", postgresql.JSONB(), nullable=True),
    )
    op.create_index("ix_health_checks_api_id", "health_checks", ["api_id"])
    op.create_index("ix_health_checks_api_id_checked_at", "health_checks", ["api_id", "checked_at"])

    # ── forecast_models ──────────────────────────────────────────
    op.create_table(
        "forecast_models",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("api_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_endpoints.id"), nullable=False),
        sa.Column("model_type", sa.String(30), server_default="prophet"),
        sa.Column("model_path", sa.String(500), nullable=False),
        sa.Column("training_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("training_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("training_samples", sa.Integer(), nullable=False),
        sa.Column("mae", sa.Float(), nullable=True),
        sa.Column("mape", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
    )
    op.create_index("ix_forecast_models_api_id", "forecast_models", ["api_id"])

    # ── forecast_results ─────────────────────────────────────────
    op.create_table(
        "forecast_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("forecast_models.id"), nullable=False),
        sa.Column("api_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_endpoints.id"), nullable=False),
        sa.Column("forecast_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("predicted_requests", sa.Float(), nullable=False),
        sa.Column("lower_bound", sa.Float(), nullable=True),
        sa.Column("upper_bound", sa.Float(), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_forecast_results_model_id", "forecast_results", ["model_id"])
    op.create_index("ix_forecast_results_api_id", "forecast_results", ["api_id"])
    op.create_index("ix_forecast_results_forecast_at", "forecast_results", ["forecast_at"])


def downgrade() -> None:
    op.drop_table("forecast_results")
    op.drop_table("forecast_models")
    op.drop_table("health_checks")
    op.drop_table("error_logs")
    op.drop_table("request_logs")
    op.drop_table("api_endpoint_tags")
    op.drop_table("api_tags")
    op.drop_table("api_versions")
    op.drop_table("api_endpoints")
    op.drop_table("api_keys")
    op.drop_table("users")
    op.drop_table("teams")
