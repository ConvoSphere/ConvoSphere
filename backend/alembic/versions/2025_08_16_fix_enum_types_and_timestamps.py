"""Fix enum types and timestamp constraints

Revision ID: 2025_08_16_fix_enum_types_and_timestamps
Revises: 2025_08_14_add_agents
Create Date: 2025-08-16 08:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2025_08_16_fix_enum_types_and_timestamps'
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
            # Check current enum type
            current_type = columns['role']['type']
            
            # If it's already user_role enum, skip
            if 'user_role' in str(current_type):
                pass
            else:
                # Create the correct user_role enum if it doesn't exist
                op.execute("""
                    DO $$ BEGIN
                        CREATE TYPE user_role AS ENUM ('ADMIN', 'MANAGER', 'USER', 'GUEST');
                    EXCEPTION
                        WHEN duplicate_object THEN null;
                    END $$;
                """)
                
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
        
        # Also fix updated_at column
        op.execute("""
            ALTER TABLE audit_logs 
            ALTER COLUMN updated_at SET NOT NULL,
            ALTER COLUMN updated_at SET DEFAULT NOW()
        """)
        
        # Update any existing NULL updated_at values
        op.execute("""
            UPDATE audit_logs 
            SET updated_at = NOW() 
            WHERE updated_at IS NULL
        """)


def downgrade() -> None:
    """Revert the changes."""
    
    connection = op.get_bind()
    inspector = connection.dialect.inspector(connection)
    
    if 'users' in inspector.get_table_names():
        # Revert the users table role column back to text
        op.execute("""
            ALTER TABLE users 
            ALTER COLUMN role TYPE text
        """)
    
    if 'audit_logs' in inspector.get_table_names():
        # Revert the audit_logs timestamp constraints
        op.execute("""
            ALTER TABLE audit_logs 
            ALTER COLUMN created_at DROP NOT NULL,
            ALTER COLUMN created_at DROP DEFAULT
        """)
        
        op.execute("""
            ALTER TABLE audit_logs 
            ALTER COLUMN updated_at DROP NOT NULL,
            ALTER COLUMN updated_at DROP DEFAULT
        """)
