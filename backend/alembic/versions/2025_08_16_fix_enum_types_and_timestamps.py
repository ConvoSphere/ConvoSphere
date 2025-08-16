"""Fix enum types and timestamp constraints

Revision ID: 2025_08_16_fix_enum_types_and_timestamps
Revises: 2025_08_14_add_agents
Create Date: 2025-08-16 08:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fix_enum_types'
down_revision = 'add_password_reset_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Fix enum types and timestamp constraints."""
    
    # First, check if the users table exists and has a role column
    connection = op.get_bind()
    inspector = connection.dialect.inspector(connection)
    
    if 'users' in inspector.get_table_names():
        # Check if the role column exists and what type it has
        columns = {col['name']: col for col in inspector.get_columns('users')}
        
        if 'role' in columns:
            # The role column exists, now fix the enum types
            # Drop the old duplicate enum types if they exist
            op.execute("DROP TYPE IF EXISTS user_role CASCADE")
            
            # Rename userrole to user_role for consistency
            op.execute("ALTER TYPE userrole RENAME TO user_role")
            
            # Update the users table to use the correct enum type
            op.execute("""
                ALTER TABLE users 
                ALTER COLUMN role TYPE user_role 
                USING role::text::user_role
            """)
    
    # Fix the audit_logs table timestamp constraints if it exists
    if 'audit_logs' in inspector.get_table_names():
        # Fix the audit_logs table timestamp constraints
        op.execute("""
            ALTER TABLE audit_logs 
            ALTER COLUMN created_at SET NOT NULL,
            ALTER COLUMN created_at SET DEFAULT NOW()
        """)
        
        # Update any existing NULL created_at values
        op.execute("""
            UPDATE audit_logs 
            SET created_at = NOW() 
            WHERE created_at IS NULL
        """)


def downgrade() -> None:
    """Revert the changes."""
    
    # Revert the role column back to text
    op.execute("""
        ALTER TABLE users 
        ALTER COLUMN role TYPE text
    """)
    
    # Recreate the old user_role enum
    op.execute("""
        CREATE TYPE user_role AS ENUM ('admin', 'manager', 'user', 'guest')
    """)
    
    # Revert the users table role column
    op.execute("""
        ALTER TABLE users 
        ALTER COLUMN role TYPE user_role 
        USING role::text::user_role
    """)
    
    # Revert the audit_logs timestamp constraints
    op.execute("""
        ALTER TABLE audit_logs 
        ALTER COLUMN created_at DROP NOT NULL,
        ALTER COLUMN created_at DROP DEFAULT
    """)
    
    # Rename user_role back to userrole
    op.execute("ALTER TYPE user_role RENAME TO userrole")
