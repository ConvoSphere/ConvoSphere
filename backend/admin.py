#!/usr/bin/env python3
"""
ChatAssistant Admin CLI

A comprehensive command-line interface for managing the ChatAssistant platform.
This tool provides database management, user administration, backup/restore,
monitoring, and development utilities.

Usage:
    python admin.py [COMMAND] [OPTIONS]

Examples:
    python admin.py db migrate
    python admin.py user create-admin
    python admin.py backup create
    python admin.py monitoring health
    python admin.py config show
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def print_success(message):
    """Print success message."""
    print(f"✅ {message}")


def print_error(message):
    """Print error message."""
    print(f"❌ {message}")


def print_info(message):
    """Print info message."""
    print(f"ℹ️ {message}")


def db_migrate():
    """Run Alembic migrations (upgrade head)."""
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            check=False,
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.returncode != 0:
            print_error(result.stderr)
            sys.exit(result.returncode)
    except FileNotFoundError:
        print_error("Alembic not found. Please install alembic or run in a virtual environment with backend dependencies.")
        sys.exit(1)


def db_status():
    """Show Alembic migration status."""
    try:
        result = subprocess.run(
            ["alembic", "current"],
            check=False,
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.returncode != 0:
            print_error(result.stderr)
            sys.exit(result.returncode)
    except FileNotFoundError:
        print_error("Alembic not found. Please install alembic or run in a virtual environment with backend dependencies.")
        sys.exit(1)


def db_downgrade(revision):
    """Downgrade DB to a specific revision."""
    try:
        result = subprocess.run(
            ["alembic", "downgrade", revision],
            check=False,
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.returncode != 0:
            print_error(result.stderr)
            sys.exit(result.returncode)
    except FileNotFoundError:
        print_error("Alembic not found. Please install alembic or run in a virtual environment with backend dependencies.")
        sys.exit(1)


def backup_create(output=None):
    """Create database backup."""
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"backup_{timestamp}.sql"
    
    try:
        # Try to get database URL from environment
        db_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
        
        if db_url.startswith("postgresql://"):
            # PostgreSQL backup
            import urllib.parse
            parsed = urllib.parse.urlparse(db_url)
            host = parsed.hostname or "localhost"
            port = parsed.port or 5432
            database = parsed.path[1:] if parsed.path else "chatassistant"
            username = parsed.username or "chatassistant"
            password = parsed.password or "chatassistant_password"
            
            # Set PGPASSWORD environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = password
            
            result = subprocess.run([
                "pg_dump",
                "-h", host,
                "-p", str(port),
                "-U", username,
                "-d", database,
                "-f", output
            ], env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                print_success(f"Database backup created: {output}")
            else:
                print_error(f"Backup failed: {result.stderr}")
                sys.exit(1)
        else:
            # SQLite backup
            import shutil
            db_file = db_url.replace("sqlite:///", "")
            shutil.copy2(db_file, output)
            print_success(f"Database backup created: {output}")
            
    except Exception as e:
        print_error(f"Backup failed: {e}")
        sys.exit(1)


def backup_restore(backup_file, confirm=False):
    """Restore database from backup."""
    if not os.path.exists(backup_file):
        print_error(f"Backup file not found: {backup_file}")
        sys.exit(1)
    
    if not confirm:
        response = input(f"Are you sure you want to restore from {backup_file}? This will overwrite the current database. (y/N): ")
        if response.lower() != 'y':
            print("Restore cancelled.")
            return
    
    try:
        db_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
        
        if db_url.startswith("postgresql://"):
            # PostgreSQL restore
            import urllib.parse
            parsed = urllib.parse.urlparse(db_url)
            host = parsed.hostname or "localhost"
            port = parsed.port or 5432
            database = parsed.path[1:] if parsed.path else "chatassistant"
            username = parsed.username or "chatassistant"
            password = parsed.password or "chatassistant_password"
            
            env = os.environ.copy()
            env["PGPASSWORD"] = password
            
            result = subprocess.run([
                "psql",
                "-h", host,
                "-p", str(port),
                "-U", username,
                "-d", database,
                "-f", backup_file
            ], env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                print_success("Database restored successfully")
            else:
                print_error(f"Restore failed: {result.stderr}")
                sys.exit(1)
        else:
            # SQLite restore
            import shutil
            db_file = db_url.replace("sqlite:///", "")
            shutil.copy2(backup_file, db_file)
            print_success("Database restored successfully")
            
    except Exception as e:
        print_error(f"Restore failed: {e}")
        sys.exit(1)


def backup_list(backup_dir="."):
    """List available backups."""
    try:
        backup_files = []
        for file in os.listdir(backup_dir):
            if file.startswith("backup_") and file.endswith(".sql"):
                file_path = os.path.join(backup_dir, file)
                stat = os.stat(file_path)
                backup_files.append({
                    "name": file,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime)
                })
        
        if not backup_files:
            print("No backups found.")
            return
        
        backup_files.sort(key=lambda x: x["modified"], reverse=True)
        for backup in backup_files:
            size_mb = backup["size"] / (1024 * 1024)
            print(f"{backup['name']} | {size_mb:.1f}MB | {backup['modified']}")
            
    except Exception as e:
        print_error(f"Error listing backups: {e}")
        sys.exit(1)


def monitoring_health():
    """Check system health."""
    print("🔍 Checking system health...")
    
    # Check if backend is running
    try:
        import requests
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API: OK")
        else:
            print(f"❌ Backend API: ERROR - Status {response.status_code}")
    except ImportError:
        print("❌ Backend API: ERROR - requests module not available")
    except Exception as e:
        print(f"❌ Backend API: ERROR - {e}")
    
    # Check database connection
    try:
        result = subprocess.run(
            ["alembic", "current"],
            check=False,
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✅ Database: OK")
        else:
            print("❌ Database: ERROR")
    except FileNotFoundError:
        print("❌ Database: ERROR - Alembic not found")
    except Exception as e:
        print(f"❌ Database: ERROR - {e}")


def config_show():
    """Show current configuration."""
    print("📋 Current Configuration:")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Database URL: {os.getenv('DATABASE_URL', 'sqlite:///./test.db')}")
    print(f"Redis URL: {os.getenv('REDIS_URL', 'redis://localhost:6379')}")
    print(f"Weaviate URL: {os.getenv('WEAVIATE_URL', 'http://localhost:8080')}")
    print(f"Backend URL: {os.getenv('BACKEND_URL', 'http://localhost:8000')}")
    print(f"Upload Directory: {os.getenv('UPLOAD_DIR', './uploads')}")
    print(f"Log Level: {os.getenv('LOG_LEVEL', 'INFO')}")


def config_validate():
    """Validate configuration."""
    print("🔍 Validating configuration...")
    
    errors = []
    
    # Check required settings
    if not os.getenv("SECRET_KEY"):
        errors.append("SECRET_KEY environment variable is required")
    
    if not os.getenv("DATABASE_URL"):
        errors.append("DATABASE_URL environment variable is required")
    
    # Check file paths
    upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
    if not os.path.exists(upload_dir):
        errors.append(f"Upload directory does not exist: {upload_dir}")
    
    if errors:
        print_error("Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print_success("Configuration is valid")


def dev_quality_check():
    """Run code quality checks."""
    print("🔍 Running code quality checks...")
    
    # Format check
    result = subprocess.run(["ruff", "format", "--check", "."], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Code formatting: OK")
    else:
        print("❌ Code formatting: FAILED")
        print(result.stdout)
    
    # Linting
    result = subprocess.run(["ruff", "check", "."], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Linting: OK")
    else:
        print("❌ Linting: FAILED")
        print(result.stdout)
    
    # Security check
    result = subprocess.run(["bandit", "-r", "."], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Security check: OK")
    else:
        print("⚠️ Security check: WARNINGS")
        print(result.stdout)


def dev_api_test(url="http://localhost:8000"):
    """Run basic API tests."""
    print(f"🧪 Testing API at {url}...")
    
    try:
        import requests
        
        # Health check
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint: OK")
        else:
            print(f"❌ Health endpoint: FAILED - {response.status_code}")
        
        # API docs
        response = requests.get(f"{url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API docs: OK")
        else:
            print(f"❌ API docs: FAILED - {response.status_code}")
            
    except ImportError:
        print_error("API test failed: requests module not available")
    except Exception as e:
        print_error(f"API test failed: {e}")


def user_create_admin():
    """Create an initial admin user."""
    print("Creating admin user...")
    email = input("Email: ")
    username = input("Username: ")
    password = input("Password: ")
    first_name = input("First name (optional): ") or None
    last_name = input("Last name (optional): ") or None
    
    try:
        # Import backend dependencies
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
        from app.core.database import SessionLocal
        from app.models.user import UserRole, UserStatus
        from app.schemas.user import UserCreate
        from app.services.user_service import UserService
        
        db = SessionLocal()
        user_service = UserService(db)
        user_data = UserCreate(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
        )
        
        user = user_service.create_user(user_data)
        print_success(f"Admin user created: {user.email} ({user.id})")
        
    except ImportError as e:
        print_error(f"Backend dependencies not available: {e}")
        print_info("Please run in a backend environment with dependencies installed")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error creating admin user: {e}")
        sys.exit(1)
    finally:
        if 'db' in locals():
            db.close()


def user_list():
    """List all users."""
    try:
        # Import backend dependencies
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
        from app.core.database import SessionLocal
        from app.models.user import UserRole
        from app.services.user_service import UserService
        
        db = SessionLocal()
        user_service = UserService(db)
        
        # Dummy current_user mit Super-Admin-Rechten für vollständige Liste
        class DummyUser:
            role = UserRole.SUPER_ADMIN
            organization_id = None

            def has_permission(self, perm):
                return True

        search_params = type(
            "Search",
            (),
            {
                "query": None,
                "role": None,
                "status": None,
                "auth_provider": None,
                "organization_id": None,
                "group_id": None,
                "is_verified": None,
                "created_after": None,
                "created_before": None,
                "last_login_after": None,
                "last_login_before": None,
                "page": 1,
                "size": 100,
            },
        )()
        
        users = user_service.list_users(search_params, DummyUser()).users
        print(f"Found {len(users)} users:")
        print("-" * 80)
        print(f"{'ID':<36} {'Email':<25} {'Username':<15} {'Role':<12} {'Status':<10}")
        print("-" * 80)
        
        for user in users:
            print(f"{user.id:<36} {user.email:<25} {user.username:<15} {user.role:<12} {user.status:<10}")
            
    except ImportError as e:
        print_error(f"Backend dependencies not available: {e}")
        print_info("Please run in a backend environment with dependencies installed")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error listing users: {e}")
        sys.exit(1)
    finally:
        if 'db' in locals():
            db.close()


def user_show(identifier):
    """Show user details."""
    try:
        # Import backend dependencies
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
        from app.core.database import SessionLocal
        from app.services.user_service import UserService
        
        db = SessionLocal()
        user_service = UserService(db)
        
        # Try to find user by different identifiers
        user = None
        if '@' in identifier:
            user = user_service.get_user_by_email(identifier)
        else:
            # Try as username first, then as ID
            user = user_service.get_user_by_username(identifier)
            if not user:
                user = user_service.get_user_by_id(identifier)
        
        if not user:
            print_error(f"User not found: {identifier}")
            sys.exit(1)
        
        print(f"User Details for: {identifier}")
        print("=" * 50)
        print(f"ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Username: {user.username}")
        print(f"Full Name: {user.first_name} {user.last_name}".strip())
        print(f"Role: {user.role}")
        print(f"Status: {user.status}")
        print(f"Verified: {user.is_verified}")
        print(f"Created: {user.created_at}")
        print(f"Last Login: {user.last_login or 'Never'}")
        print(f"Organization: {user.organization_id or 'None'}")
        print(f"Department: {user.department or 'None'}")
        print(f"Job Title: {user.job_title or 'None'}")
        
    except ImportError as e:
        print_error(f"Backend dependencies not available: {e}")
        print_info("Please run in a backend environment with dependencies installed")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error showing user: {e}")
        sys.exit(1)
    finally:
        if 'db' in locals():
            db.close()


def user_create(email, username, password, first_name=None, last_name=None, role="user", status="active"):
    """Create a new user."""
    try:
        # Import backend dependencies
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
        from app.core.database import SessionLocal
        from app.models.user import UserRole, UserStatus
        from app.schemas.user import UserCreate
        from app.services.user_service import UserService
        
        db = SessionLocal()
        user_service = UserService(db)
        
        # Convert string to enum
        role_enum = UserRole(role)
        status_enum = UserStatus(status)
        
        user_data = UserCreate(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role_enum,
            status=status_enum,
        )
        
        user = user_service.create_user(user_data)
        print_success(f"User created: {user.email} ({user.id})")
        print(f"Role: {user.role}")
        print(f"Status: {user.status}")
        
    except ImportError as e:
        print_error(f"Backend dependencies not available: {e}")
        print_info("Please run in a backend environment with dependencies installed")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error creating user: {e}")
        sys.exit(1)
    finally:
        if 'db' in locals():
            db.close()


def user_update(identifier, **kwargs):
    """Update user."""
    try:
        # Import backend dependencies
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
        from app.core.database import SessionLocal
        from app.models.user import UserRole, UserStatus
        from app.schemas.user import UserUpdate
        from app.services.user_service import UserService
        
        db = SessionLocal()
        user_service = UserService(db)
        
        # Try to find user by different identifiers
        user = None
        if '@' in identifier:
            user = user_service.get_user_by_email(identifier)
        else:
            # Try as username first, then as ID
            user = user_service.get_user_by_username(identifier)
            if not user:
                user = user_service.get_user_by_id(identifier)
        
        if not user:
            print_error(f"User not found: {identifier}")
            sys.exit(1)
        
        # Prepare update data
        update_data = {}
        if kwargs.get('email'):
            update_data['email'] = kwargs['email']
        if kwargs.get('username'):
            update_data['username'] = kwargs['username']
        if kwargs.get('first_name'):
            update_data['first_name'] = kwargs['first_name']
        if kwargs.get('last_name'):
            update_data['last_name'] = kwargs['last_name']
        if kwargs.get('role'):
            update_data['role'] = UserRole(kwargs['role'])
        if kwargs.get('status'):
            update_data['status'] = UserStatus(kwargs['status'])
        
        if not update_data:
            print_error("No update data provided")
            sys.exit(1)
        
        # Create dummy current user for permissions
        class DummyUser:
            role = UserRole.SUPER_ADMIN
            organization_id = None

            def has_permission(self, perm):
                return True
        
        user_update_obj = UserUpdate(**update_data)
        updated_user = user_service.update_user(user.id, user_update_obj, DummyUser())
        
        print_success(f"User updated: {updated_user.email}")
        print("Updated fields:")
        for field, value in update_data.items():
            print(f"  {field}: {value}")
        
    except ImportError as e:
        print_error(f"Backend dependencies not available: {e}")
        print_info("Please run in a backend environment with dependencies installed")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error updating user: {e}")
        sys.exit(1)
    finally:
        if 'db' in locals():
            db.close()


def user_delete(identifier, confirm=False):
    """Delete user."""
    if not confirm:
        response = input(f"Are you sure you want to delete user {identifier}? This action cannot be undone. (y/N): ")
        if response.lower() != 'y':
            print("Delete cancelled.")
            return
    
    try:
        # Import backend dependencies
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
        from app.core.database import SessionLocal
        from app.models.user import UserRole
        from app.services.user_service import UserService
        
        db = SessionLocal()
        user_service = UserService(db)
        
        # Try to find user by different identifiers
        user = None
        if '@' in identifier:
            user = user_service.get_user_by_email(identifier)
        else:
            # Try as username first, then as ID
            user = user_service.get_user_by_username(identifier)
            if not user:
                user = user_service.get_user_by_id(identifier)
        
        if not user:
            print_error(f"User not found: {identifier}")
            sys.exit(1)
        
        # Create dummy current user for permissions
        class DummyUser:
            role = UserRole.SUPER_ADMIN
            organization_id = None

            def has_permission(self, perm):
                return True
        
        success = user_service.delete_user(user.id, DummyUser())
        
        if success:
            print_success(f"User deleted: {user.email}")
        else:
            print_error("Failed to delete user")
            sys.exit(1)
        
    except ImportError as e:
        print_error(f"Backend dependencies not available: {e}")
        print_info("Please run in a backend environment with dependencies installed")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error deleting user: {e}")
        sys.exit(1)
    finally:
        if 'db' in locals():
            db.close()


def user_reset_password():
    """Reset user password."""
    email = input("User email: ")
    new_password = input("New password: ")
    
    try:
        # Import backend dependencies
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
        from app.core.database import SessionLocal
        from app.schemas.user import UserPasswordUpdate
        from app.services.user_service import UserService
        
        db = SessionLocal()
        user_service = UserService(db)
        
        user = user_service.get_user_by_email(email)
        if not user:
            print_error(f"User not found: {email}")
            sys.exit(1)
        
        password_data = UserPasswordUpdate(
            current_password="",  # Not needed for admin reset
            new_password=new_password
        )
        
        success = user_service.update_password(user.id, password_data)
        
        if success:
            print_success(f"Password reset for user: {email}")
        else:
            print_error("Failed to reset password")
            sys.exit(1)
        
    except ImportError as e:
        print_error(f"Backend dependencies not available: {e}")
        print_info("Please run in a backend environment with dependencies installed")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error resetting password: {e}")
        sys.exit(1)
    finally:
        if 'db' in locals():
            db.close()


def show_help():
    """Show help message."""
    print("ChatAssistant Admin CLI")
    print("=" * 50)
    print()
    print("Available commands:")
    print()
    print("Database Management:")
    print("  db migrate              Run database migrations")
    print("  db status               Show migration status")
    print("  db downgrade <rev>      Downgrade to revision")
    print()
    print("User Management:")
    print("  user create-admin       Create admin user")
    print("  user list               List all users")
    print("  user show <id>          Show user details")
    print("  user create             Create new user")
    print("  user update <id>        Update user")
    print("  user delete <id>        Delete user")
    print("  user reset-password     Reset user password")
    print()
    print("Backup & Recovery:")
    print("  backup create           Create database backup")
    print("  backup restore <file>   Restore from backup")
    print("  backup list             List available backups")
    print()
    print("Monitoring:")
    print("  monitoring health       Check system health")
    print()
    print("Configuration:")
    print("  config show             Show current configuration")
    print("  config validate         Validate configuration")
    print()
    print("Development:")
    print("  dev quality-check       Run code quality checks")
    print("  dev api-test            Run API tests")
    print()
    print("Examples:")
    print("  python3 admin.py db migrate")
    print("  python3 admin.py user create-admin")
    print("  python3 admin.py user list")
    print("  python3 admin.py backup create")
    print("  python3 admin.py monitoring health")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="ChatAssistant Admin CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Database commands
    db_parser = subparsers.add_parser("db", help="Database management")
    db_subparsers = db_parser.add_subparsers(dest="db_command")
    db_subparsers.add_parser("migrate", help="Run migrations")
    db_subparsers.add_parser("status", help="Show migration status")
    
    downgrade_parser = db_subparsers.add_parser("downgrade", help="Downgrade to revision")
    downgrade_parser.add_argument("revision", help="Revision to downgrade to")
    
    # User commands
    user_parser = subparsers.add_parser("user", help="User management")
    user_subparsers = user_parser.add_subparsers(dest="user_command")
    user_subparsers.add_parser("create-admin", help="Create admin user")
    user_subparsers.add_parser("list", help="List all users")
    user_subparsers.add_parser("reset-password", help="Reset user password")
    
    # User show command
    show_parser = user_subparsers.add_parser("show", help="Show user details")
    show_parser.add_argument("identifier", help="User email, username, or ID")
    
    # User update command
    update_parser = user_subparsers.add_parser("update", help="Update user")
    update_parser.add_argument("identifier", help="User email, username, or ID")
    update_parser.add_argument("--email", help="New email")
    update_parser.add_argument("--username", help="New username")
    update_parser.add_argument("--first-name", help="First name")
    update_parser.add_argument("--last-name", help="Last name")
    update_parser.add_argument("--role", choices=["user", "admin", "super_admin"], help="User role")
    update_parser.add_argument("--status", choices=["active", "inactive", "suspended"], help="User status")
    
    # User delete command
    delete_parser = user_subparsers.add_parser("delete", help="Delete user")
    delete_parser.add_argument("identifier", help="User email, username, or ID")
    delete_parser.add_argument("--confirm", action="store_true", help="Skip confirmation")
    
    # User create command
    create_parser = user_subparsers.add_parser("create", help="Create new user")
    create_parser.add_argument("--email", required=True, help="User email")
    create_parser.add_argument("--username", required=True, help="Username")
    create_parser.add_argument("--password", required=True, help="Password")
    create_parser.add_argument("--first-name", help="First name")
    create_parser.add_argument("--last-name", help="Last name")
    create_parser.add_argument("--role", choices=["user", "admin", "super_admin"], default="user", help="User role")
    create_parser.add_argument("--status", choices=["active", "inactive", "suspended"], default="active", help="User status")
    
    # Backup commands
    backup_parser = subparsers.add_parser("backup", help="Backup and recovery")
    backup_subparsers = backup_parser.add_subparsers(dest="backup_command")
    
    create_parser = backup_subparsers.add_parser("create", help="Create backup")
    create_parser.add_argument("--output", help="Output file path")
    
    restore_parser = backup_subparsers.add_parser("restore", help="Restore from backup")
    restore_parser.add_argument("backup_file", help="Backup file to restore")
    restore_parser.add_argument("--confirm", action="store_true", help="Skip confirmation")
    
    list_parser = backup_subparsers.add_parser("list", help="List backups")
    list_parser.add_argument("--backup-dir", default=".", help="Backup directory")
    
    # Monitoring commands
    monitoring_parser = subparsers.add_parser("monitoring", help="System monitoring")
    monitoring_subparsers = monitoring_parser.add_subparsers(dest="monitoring_command")
    monitoring_subparsers.add_parser("health", help="Check system health")
    
    # Config commands
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_subparsers = config_parser.add_subparsers(dest="config_command")
    config_subparsers.add_parser("show", help="Show configuration")
    config_subparsers.add_parser("validate", help="Validate configuration")
    
    # Dev commands
    dev_parser = subparsers.add_parser("dev", help="Development tools")
    dev_subparsers = dev_parser.add_subparsers(dest="dev_command")
    
    dev_subparsers.add_parser("quality-check", help="Run code quality checks")
    
    api_test_parser = dev_subparsers.add_parser("api-test", help="Run API tests")
    api_test_parser.add_argument("--url", default="http://localhost:8000", help="API URL")
    
    args = parser.parse_args()
    
    if not args.command:
        show_help()
        return
    
    # Execute commands
    if args.command == "db":
        if args.db_command == "migrate":
            db_migrate()
        elif args.db_command == "status":
            db_status()
        elif args.db_command == "downgrade":
            db_downgrade(args.revision)
    
    elif args.command == "user":
        if args.user_command == "create-admin":
            user_create_admin()
        elif args.user_command == "list":
            user_list()
        elif args.user_command == "show":
            user_show(args.identifier)
        elif args.user_command == "create":
            user_create(
                email=args.email,
                username=args.username,
                password=args.password,
                first_name=args.first_name,
                last_name=args.last_name,
                role=args.role,
                status=args.status
            )
        elif args.user_command == "update":
            update_data = {}
            if args.email:
                update_data['email'] = args.email
            if args.username:
                update_data['username'] = args.username
            if args.first_name:
                update_data['first_name'] = args.first_name
            if args.last_name:
                update_data['last_name'] = args.last_name
            if args.role:
                update_data['role'] = args.role
            if args.status:
                update_data['status'] = args.status
            user_update(args.identifier, **update_data)
        elif args.user_command == "delete":
            user_delete(args.identifier, args.confirm)
        elif args.user_command == "reset-password":
            user_reset_password()
    
    elif args.command == "backup":
        if args.backup_command == "create":
            backup_create(args.output)
        elif args.backup_command == "restore":
            backup_restore(args.backup_file, args.confirm)
        elif args.backup_command == "list":
            backup_list(args.backup_dir)
    
    elif args.command == "monitoring":
        if args.monitoring_command == "health":
            monitoring_health()
    
    elif args.command == "config":
        if args.config_command == "show":
            config_show()
        elif args.config_command == "validate":
            config_validate()
    
    elif args.command == "dev":
        if args.dev_command == "quality-check":
            dev_quality_check()
        elif args.dev_command == "api-test":
            dev_api_test(args.url)


if __name__ == "__main__":
    main()