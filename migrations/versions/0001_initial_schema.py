"""Initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-27
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("is_premium", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("premium_until", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("idx_users_email", "users", ["email"])
    op.create_index("idx_users_created_at", "users", ["created_at"])

    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("target_url", sa.Text(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("click_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("code", name="uq_links_code"),
    )
    op.create_index("idx_links_user_id", "links", ["user_id"])
    op.create_index("idx_links_code", "links", ["code"])
    op.create_index("idx_links_created_at", "links", ["created_at"])
    op.create_index("idx_links_is_active", "links", ["is_active"])

    op.create_table(
        "link_analytics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("link_id", sa.Integer(), nullable=False),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("referer", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("country", sa.String(length=2), nullable=True),
        sa.Column("clicked_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["link_id"], ["links.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_analytics_link_id", "link_analytics", ["link_id"])
    op.create_index("idx_analytics_clicked_at", "link_analytics", ["clicked_at"])
    op.create_index("idx_analytics_ip", "link_analytics", ["ip_address"])


def downgrade() -> None:
    op.drop_index("idx_analytics_ip", table_name="link_analytics")
    op.drop_index("idx_analytics_clicked_at", table_name="link_analytics")
    op.drop_index("idx_analytics_link_id", table_name="link_analytics")
    op.drop_table("link_analytics")

    op.drop_index("idx_links_is_active", table_name="links")
    op.drop_index("idx_links_created_at", table_name="links")
    op.drop_index("idx_links_code", table_name="links")
    op.drop_index("idx_links_user_id", table_name="links")
    op.drop_table("links")

    op.drop_index("idx_users_created_at", table_name="users")
    op.drop_index("idx_users_email", table_name="users")
    op.drop_table("users")
