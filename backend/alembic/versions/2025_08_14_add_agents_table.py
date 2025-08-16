"""add agents table with planning fields

Revision ID: 2025_08_14_add_agents
Revises: c02ce5c4f07b_create_all_tables
Create Date: 2025-08-14 01:45:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2025_08_14_add_agents"
down_revision = "ad2434bca38f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_template", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("tools", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=False, server_default="gpt-4"),
        sa.Column("temperature", sa.Float(), nullable=False, server_default="0.7"),
        sa.Column("max_tokens", sa.String(length=50), nullable=True),
        sa.Column("max_context_length", sa.String(length=50), nullable=True),
        sa.Column("personality", sa.Text(), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("planning_strategy", sa.String(length=50), nullable=False, server_default="none"),
        sa.Column("max_planning_steps", sa.String(length=10), nullable=True),
        sa.Column("abort_criteria", postgresql.JSON(astext_type=sa.Text()), nullable=True),
    )
    op.create_index("ix_agents_name", "agents", ["name"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_agents_name", table_name="agents")
    op.drop_table("agents")