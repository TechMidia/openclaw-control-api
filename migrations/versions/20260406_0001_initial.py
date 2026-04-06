"""initial schema

Revision ID: 20260406_0001
Revises:
Create Date: 2026-04-06
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260406_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=50), nullable=False, unique=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "sessions_audit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sessions_audit_user_id", "sessions_audit", ["user_id"])

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("latest_status", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_projects_slug", "projects", ["slug"], unique=True)

    op.create_table(
        "operations_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_instance", sa.String(length=120), nullable=True),
        sa.Column("operation_date", sa.String(length=32), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_operations_snapshots_source_instance", "operations_snapshots", ["source_instance"])
    op.create_index("ix_operations_snapshots_operation_date", "operations_snapshots", ["operation_date"])

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "operation_snapshot_id",
            sa.Integer(),
            sa.ForeignKey("operations_snapshots.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tasks_operation_snapshot_id", "tasks", ["operation_snapshot_id"])
    op.create_index("ix_tasks_project_id", "tasks", ["project_id"])

    op.create_table(
        "financial_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_instance", sa.String(length=120), nullable=True),
        sa.Column("cash_position", sa.String(length=120), nullable=True),
        sa.Column("receivables_summary", sa.String(length=120), nullable=True),
        sa.Column("payables_summary", sa.String(length=120), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "receivables",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "financial_snapshot_id",
            sa.Integer(),
            sa.ForeignKey("financial_snapshots.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("due_date", sa.String(length=32), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
    )
    op.create_index("ix_receivables_financial_snapshot_id", "receivables", ["financial_snapshot_id"])

    op.create_table(
        "payables",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "financial_snapshot_id",
            sa.Integer(),
            sa.ForeignKey("financial_snapshots.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("due_date", sa.String(length=32), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
    )
    op.create_index("ix_payables_financial_snapshot_id", "payables", ["financial_snapshot_id"])

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=120), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_alerts_source", "alerts", ["source"])

    op.create_table(
        "decisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=120), nullable=False),
        sa.Column("decision", sa.Text(), nullable=False),
        sa.Column("owner", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_decisions_source", "decisions", ["source"])

    op.create_table(
        "agents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("agent_id", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("last_heartbeat", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_agents_agent_id", "agents", ["agent_id"], unique=True)

    op.create_table(
        "heartbeats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("agent_id", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("source_file", sa.String(length=255), nullable=True),
        sa.Column("at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_heartbeats_agent_id", "heartbeats", ["agent_id"])

    op.create_table(
        "governance_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_instance", sa.String(length=120), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "consumption_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_instance", sa.String(length=120), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "ingest_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("block", sa.String(length=50), nullable=False),
        sa.Column("source_instance", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("payload_size", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ingest_logs_block", "ingest_logs", ["block"])
    op.create_index("ix_ingest_logs_source_instance", "ingest_logs", ["source_instance"])


def downgrade() -> None:
    op.drop_index("ix_ingest_logs_source_instance", table_name="ingest_logs")
    op.drop_index("ix_ingest_logs_block", table_name="ingest_logs")
    op.drop_table("ingest_logs")
    op.drop_table("consumption_snapshots")
    op.drop_table("governance_snapshots")
    op.drop_index("ix_heartbeats_agent_id", table_name="heartbeats")
    op.drop_table("heartbeats")
    op.drop_index("ix_agents_agent_id", table_name="agents")
    op.drop_table("agents")
    op.drop_index("ix_decisions_source", table_name="decisions")
    op.drop_table("decisions")
    op.drop_index("ix_alerts_source", table_name="alerts")
    op.drop_table("alerts")
    op.drop_index("ix_payables_financial_snapshot_id", table_name="payables")
    op.drop_table("payables")
    op.drop_index("ix_receivables_financial_snapshot_id", table_name="receivables")
    op.drop_table("receivables")
    op.drop_table("financial_snapshots")
    op.drop_index("ix_tasks_project_id", table_name="tasks")
    op.drop_index("ix_tasks_operation_snapshot_id", table_name="tasks")
    op.drop_table("tasks")
    op.drop_index("ix_operations_snapshots_operation_date", table_name="operations_snapshots")
    op.drop_index("ix_operations_snapshots_source_instance", table_name="operations_snapshots")
    op.drop_table("operations_snapshots")
    op.drop_index("ix_projects_slug", table_name="projects")
    op.drop_table("projects")
    op.drop_index("ix_sessions_audit_user_id", table_name="sessions_audit")
    op.drop_table("sessions_audit")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
    op.drop_table("roles")

