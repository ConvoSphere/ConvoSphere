"""Add password reset fields to user model

Revision ID: add_password_reset_fields
Revises: c02ce5c4f07b
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_password_reset_fields'
down_revision = 'c02ce5c4f07b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add password reset fields to users table."""
    # Add password reset token field
    op.add_column('users', sa.Column('password_reset_token', sa.String(255), nullable=True))
    
    # Add password reset expiration field
    op.add_column('users', sa.Column('password_reset_expires_at', sa.DateTime(timezone=True), nullable=True))
    
    # Create index on password_reset_token for faster lookups
    op.create_index(op.f('ix_users_password_reset_token'), 'users', ['password_reset_token'], unique=False)


def downgrade() -> None:
    """Remove password reset fields from users table."""
    # Drop index
    op.drop_index(op.f('ix_users_password_reset_token'), table_name='users')
    
    # Drop columns
    op.drop_column('users', 'password_reset_expires_at')
    op.drop_column('users', 'password_reset_token')