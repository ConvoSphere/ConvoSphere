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
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


def print_success(message):
    """Print success message."""


def print_error(message):
    """Print error message."""


def print_info(message):
    """Print info message."""


def db_migrate():
    """Run Alembic migrations (upgrade head)."""
    try:
        alembic_path = shutil.which("alembic")
        if not alembic_path:
            print_error(
                "Alembic not found in PATH. Please install alembic or run in a virtual environment with backend dependencies."
            )
            sys.exit(1)

        result = subprocess.run(
            [alembic_path, "upgrade", "head"],
            check=False,
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print_error(result.stderr)
            sys.exit(result.returncode)
    except FileNotFoundError:
        print_error(
            "Alembic not found. Please install alembic or run in a virtual environment with backend dependencies.",
        )
        sys.exit(1)


def db_status():
    """Show Alembic migration status."""
    try:
        alembic_path = shutil.which("alembic")
        if not alembic_path:
            print_error(
                "Alembic not found in PATH. Please install alembic or run in a virtual environment with backend dependencies."
            )
            sys.exit(1)

        result = subprocess.run(
            [alembic_path, "current"],
            check=False,
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print_error(result.stderr)
            sys.exit(result.returncode)
    except FileNotFoundError:
        print_error(
            "Alembic not found. Please install alembic or run in a virtual environment with backend dependencies.",
        )
        sys.exit(1)


def db_downgrade(revision):
    """Downgrade DB to a specific revision."""
    try:
        alembic_path = shutil.which("alembic")
        if not alembic_path:
            print_error(
                "Alembic not found in PATH. Please install alembic or run in a virtual environment with backend dependencies."
            )
            sys.exit(1)

        result = subprocess.run(
            [alembic_path, "downgrade", revision],
            check=False,
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print_error(result.stderr)
            sys.exit(result.returncode)
    except FileNotFoundError:
        print_error(
            "Alembic not found. Please install alembic or run in a virtual environment with backend dependencies.",
        )
        sys.exit(1)


def db_test_connection():
    """Test database connection."""
    try:
        # Import database engine from cli.py approach
        from sqlalchemy import create_engine, text

        from backend.app.core.config import settings

        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print_success("Database connection successful")
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        sys.exit(1)


def db_info():
    """Show database information."""
    try:
        from sqlalchemy import create_engine, text

        from backend.app.core.config import settings

        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            # Get database name
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print_info(f"Database: {db_name}")

            # Get table count
            result = conn.execute(
                text(
                    """
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_schema = 'public'
            """
                ),
            )
            table_count = result.scalar()
            print_info(f"Tables: {table_count}")

            # Get user count
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            print_info(f"Users: {user_count}")

    except Exception as e:
        print_error(f"Error getting database info: {e}")
        sys.exit(1)


def db_reset(confirm=False):
    """Completely reset the database - drop all tables and recreate them."""
    if not confirm:
        response = input(
            "⚠️  WARNING: This will completely delete all data in the database. "
            "This action cannot be undone. Are you sure? (yes/no): ",
        )
        if response.lower() != "yes":
            return

    try:
        from sqlalchemy import create_engine, text

        from backend.app.core.config import settings

        engine = create_engine(settings.database_url)

        # Step 1: Drop all tables
        with engine.connect() as conn:
            # Disable foreign key checks temporarily
            conn.execute(text("SET session_replication_role = replica;"))

            # Get all table names
            result = conn.execute(
                text(
                    """
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
                AND tablename != 'alembic_version'
            """
                )
            )
            tables = [row[0] for row in result]

            # Drop all tables
            for table in tables:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))

            # Re-enable foreign key checks
            conn.execute(text("SET session_replication_role = DEFAULT;"))
            conn.commit()

        # Step 2: Reset Alembic version table
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
            conn.commit()

        # Step 3: Run migrations to recreate all tables
        db_migrate()

        print_success("Database has been completely reset and reinitialized")

    except Exception as e:
        print_error(f"Database reset failed: {e}")
        sys.exit(1)


def db_clear_data(confirm=False):
    """Clear all data from tables but keep the structure."""
    if not confirm:
        response = input(
            "⚠️  WARNING: This will delete all data from all tables but keep the structure. "
            "This action cannot be undone. Are you sure? (yes/no): ",
        )
        if response.lower() != "yes":
            return

    try:
        from sqlalchemy import create_engine, text

        from backend.app.core.config import settings

        engine = create_engine(settings.database_url)

        with engine.connect() as conn:
            # Disable foreign key checks temporarily
            conn.execute(text("SET session_replication_role = replica;"))

            # Get all table names
            result = conn.execute(
                text(
                    """
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
                AND tablename != 'alembic_version'
            """
                )
            )
            tables = [row[0] for row in result]

            # Truncate all tables
            for table in tables:
                conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))

            # Re-enable foreign key checks
            conn.execute(text("SET session_replication_role = DEFAULT;"))
            conn.commit()

        print_success("All data has been cleared from the database")

    except Exception as e:
        print_error(f"Data clearing failed: {e}")
        sys.exit(1)


def backup_create(output=None):
    """Create database backup."""
    if not output:
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
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
            database = parsed.path[1:] if parsed.path else "convosphere"
            username = parsed.username or "convosphere"
            password = parsed.password or "convosphere_password"

            # Set PGPASSWORD environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = password

            pg_dump_path = shutil.which("pg_dump")
            if not pg_dump_path:
                print_error(
                    "pg_dump not found in PATH. Please install PostgreSQL client tools."
                )
                sys.exit(1)

            result = subprocess.run(
                [
                    pg_dump_path,
                    "-h",
                    host,
                    "-p",
                    str(port),
                    "-U",
                    username,
                    "-d",
                    database,
                    "-f",
                    output,
                ],
                check=False,
                env=env,
                capture_output=True,
                text=True,
            )

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
    if not Path(backup_file).exists():
        print_error(f"Backup file not found: {backup_file}")
        sys.exit(1)

    if not confirm:
        response = input(
            f"Are you sure you want to restore from {backup_file}? This will overwrite the current database. (y/N): ",
        )
        if response.lower() != "y":
            return

    try:
        db_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")

        if db_url.startswith("postgresql://"):
            # PostgreSQL restore
            import urllib.parse

            parsed = urllib.parse.urlparse(db_url)
            host = parsed.hostname or "localhost"
            port = parsed.port or 5432
            database = parsed.path[1:] if parsed.path else "convosphere"
            username = parsed.username or "convosphere"
            password = parsed.password or "convosphere_password"

            env = os.environ.copy()
            env["PGPASSWORD"] = password

            psql_path = shutil.which("psql")
            if not psql_path:
                print_error(
                    "psql not found in PATH. Please install PostgreSQL client tools."
                )
                sys.exit(1)

            result = subprocess.run(
                [
                    psql_path,
                    "-h",
                    host,
                    "-p",
                    str(port),
                    "-U",
                    username,
                    "-d",
                    database,
                    "-f",
                    backup_file,
                ],
                check=False,
                env=env,
                capture_output=True,
                text=True,
            )

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
                backup_files.append(
                    {
                        "name": file,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime),
                    },
                )

        if not backup_files:
            return

        backup_files.sort(key=lambda x: x["modified"], reverse=True)
        for backup in backup_files:
            backup["size"] / (1024 * 1024)

    except Exception as e:
        print_error(f"Error listing backups: {e}")
        sys.exit(1)


def monitoring_health():
    """Check system health."""

    # Check if backend is running
    try:
        import requests

        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            print_success("Backend health check passed")
        else:
            print_error(f"Backend health check failed: {response.status_code}")
    except ImportError:
        print_error("requests module not available")
    except Exception as e:
        print_error(f"Health check error: {e}")

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
            print_success("Database connection check passed")
        else:
            print_error(f"Database connection check failed: {result.stderr}")
    except FileNotFoundError:
        print_error("alembic command not found")
    except Exception as e:
        print_error(f"Database check error: {e}")


def monitoring_logs(lines=50, level="INFO"):
    """Show recent application logs."""
    try:
        from backend.app.core.config import settings

        log_file = settings.log_file
        if not os.path.exists(log_file):
            print_error(f"Log file not found: {log_file}")
            return

        with open(log_file) as f:
            log_lines = f.readlines()

        # Filter by level and get last N lines
        filtered_lines = [line for line in log_lines if level in line]
        recent_lines = (
            filtered_lines[-lines:] if len(filtered_lines) > lines else filtered_lines
        )

        if recent_lines:
            print_info(f"Recent {level} logs (last {len(recent_lines)} lines):")
            for _line in recent_lines:
                pass
        else:
            print_info(f"No {level} logs found in recent {lines} lines")

    except Exception as e:
        print_error(f"Error reading logs: {e}")


def config_show():
    """Show current configuration."""


def config_validate():
    """Validate configuration."""

    errors = []

    # Check required settings
    if not os.getenv("SECRET_KEY"):
        errors.append("SECRET_KEY environment variable is required")

    if not os.getenv("DATABASE_URL"):
        errors.append("DATABASE_URL environment variable is required")

    # Check file paths
    upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
    if not Path(upload_dir).exists():
        errors.append(f"Upload directory does not exist: {upload_dir}")

    if errors:
        print_error("Configuration validation failed:")
        for error in errors:
            print_error(f"  - {error}")
        sys.exit(1)
    else:
        print_success("Configuration is valid")


def dev_quality_check():
    """Run code quality checks."""

    # Format check
    result = subprocess.run(
        ["ruff", "format", "--check", "."],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print_success("Code formatting check passed")
    else:
        print_error(f"Code formatting check failed: {result.stderr}")

    # Linting
    result = subprocess.run(
        ["ruff", "check", "."], check=False, capture_output=True, text=True
    )
    if result.returncode == 0:
        print_success("Code linting check passed")
    else:
        print_error(f"Code linting check failed: {result.stderr}")

    # Security check
    result = subprocess.run(
        ["bandit", "-r", "."], check=False, capture_output=True, text=True
    )
    if result.returncode == 0:
        print_success("Security check passed")
    else:
        print_error(f"Security check failed: {result.stderr}")


def dev_api_test(url="http://localhost:8000"):
    """Run basic API tests."""

    try:
        import requests

        # Health check
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            print_success("Health check: OK")
        else:
            print_error(f"Health check failed: {response.status_code}")

        # API docs
        response = requests.get(f"{url}/docs", timeout=5)
        if response.status_code == 200:
            print_success("API docs: OK")
        else:
            print_error(f"API docs failed: {response.status_code}")

    except ImportError:
        print_error("API test failed: requests module not available")
    except Exception as e:
        print_error(f"API test failed: {e}")


def dev_test_data(users=5):
    """Create test data for development."""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from backend.app.core.config import settings
        from backend.app.models.user import UserRole, UserStatus
        from backend.app.schemas.user import UserCreate
        from backend.app.services.user_service import UserService

        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        user_service = UserService(db)

        for i in range(users):
            user_data = UserCreate(
                email=f"test{i}@example.com",
                username=f"testuser{i}",
                password="testpass123",
                first_name=f"Test{i}",
                last_name="User",
                role=UserRole.USER,
                status=UserStatus.ACTIVE,
            )
            user_service.create_user(user_data)

        print_success(f"Created {users} test users successfully")

    except Exception as e:
        print_error(f"Error creating test data: {e}")
        sys.exit(1)
    finally:
        if "db" in locals():
            db.close()


def user_create_admin():
    """Create an initial admin user with secure password validation."""
    import getpass
    import re

    print_info("Creating admin user...")
    print_info("Password requirements:")
    print_info("- At least 8 characters long")
    print_info("- Contains at least one uppercase letter")
    print_info("- Contains at least one lowercase letter")
    print_info("- Contains at least one number")
    print_info("- Contains at least one special character")

    email = input("Email: ").strip()
    username = input("Username: ").strip()

    # Secure password input
    password = getpass.getpass("Password: ")
    password_confirm = getpass.getpass("Confirm password: ")

    if password != password_confirm:
        print_error("Passwords do not match")
        return

    # Password validation
    if len(password) < 8:
        print_error("Password must be at least 8 characters long")
        return

    if not re.search(r"[A-Z]", password):
        print_error("Password must contain at least one uppercase letter")
        return

    if not re.search(r"[a-z]", password):
        print_error("Password must contain at least one lowercase letter")
        return

    if not re.search(r"\d", password):
        print_error("Password must contain at least one number")
        return

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        print_error("Password must contain at least one special character")
        return

    first_name = input("First name (optional): ").strip() or None
    last_name = input("Last name (optional): ").strip() or None

    try:
        # Import backend dependencies
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
        from backend.app.core.database import SessionLocal
        from backend.app.models.user import UserRole, UserStatus
        from backend.app.schemas.user import UserCreate
        from backend.app.services.user_service import UserService

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
        print_success(f"Admin user created successfully: {user.email} ({user.id})")
        print_info("Please keep the credentials secure and change the password after first login")

    except ImportError as e:
        print_error(f"Backend dependencies not available: {e}")
        print_info("Please run in a backend environment with dependencies installed")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error creating admin user: {e}")
        sys.exit(1)
    finally:
        if "db" in locals():
            db.close()


def user_create_secure():
    """Create a user with credentials from environment variables (for automation)."""
    try:
        # Import backend dependencies
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
        from backend.app.core.database import SessionLocal
        from backend.app.models.user import UserRole, UserStatus
        from backend.app.schemas.user import UserCreate
        from backend.app.services.user_service import UserService

        # Get credentials from environment variables
        email = os.getenv("ADMIN_EMAIL")
        username = os.getenv("ADMIN_USERNAME")
        password = os.getenv("ADMIN_PASSWORD")
        first_name = os.getenv("ADMIN_FIRST_NAME")
        last_name = os.getenv("ADMIN_LAST_NAME")
        role = os.getenv("ADMIN_ROLE", "admin")

        if not all([email, username, password]):
            print_error("ADMIN_EMAIL, ADMIN_USERNAME, and ADMIN_PASSWORD must be set")
            return

        # Validate role
        valid_roles = ["admin", "super_admin", "manager", "user"]
        if role not in valid_roles:
            print_error(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
            return

        db = SessionLocal()
        user_service = UserService(db)

        # Check if user already exists
        existing_user = user_service.get_user_by_email(email)
        if existing_user:
            print_info(f"User with email {email} already exists")
            return

        user_data = UserCreate(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=getattr(UserRole, role.upper()),
            status=UserStatus.ACTIVE,
        )

        user = user_service.create_user(user_data)
        print_success(f"User created successfully: {user.email} ({user.id}) with role {role}")

    except ImportError as e:
        print_error(f"Backend dependencies not available: {e}")
        print_info("Please run in a backend environment with dependencies installed")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error creating user: {e}")
        sys.exit(1)
    finally:
        if "db" in locals():
            db.close()


def user_list():
    """List all users."""
    try:
        # Import backend dependencies
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
        from backend.app.core.database import SessionLocal
        from backend.app.models.user import UserRole
        from backend.app.services.user_service import UserService

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

        for _user in users:
            pass

    except ImportError as e:
        print_error(f"Backend dependencies not available: {e}")
        print_info("Please run in a backend environment with dependencies installed")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error listing users: {e}")
        sys.exit(1)
    finally:
        if "db" in locals():
            db.close()


def user_show(identifier):
    """Show user details."""
    try:
        # Import backend dependencies
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
        from backend.app.core.database import SessionLocal
        from backend.app.services.user_service import UserService

        db = SessionLocal()
        user_service = UserService(db)

        # Try to find user by different identifiers
        user = None
        if "@" in identifier:
            user = user_service.get_user_by_email(identifier)
        else:
            # Try as username first, then as ID
            user = user_service.get_user_by_username(identifier)
            if not user:
                user = user_service.get_user_by_id(identifier)

        if not user:
            print_error(f"User not found: {identifier}")
            sys.exit(1)

    except ImportError as e:
        print_error(f"Backend dependencies not available: {e}")
        print_info("Please run in a backend environment with dependencies installed")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error showing user: {e}")
        sys.exit(1)
    finally:
        if "db" in locals():
            db.close()


def user_create(
    email,
    username,
    password,
    first_name=None,
    last_name=None,
    role="user",
    status="active",
):
    """Create a new user."""
    try:
        # Import backend dependencies
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
        from backend.app.core.database import SessionLocal
        from backend.app.models.user import UserRole, UserStatus
        from backend.app.schemas.user import UserCreate
        from backend.app.services.user_service import UserService

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

    except ImportError as e:
        print_error(f"Backend dependencies not available: {e}")
        print_info("Please run in a backend environment with dependencies installed")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error creating user: {e}")
        sys.exit(1)
    finally:
        if "db" in locals():
            db.close()


def user_update(identifier, **kwargs):
    """Update user."""
    try:
        # Import backend dependencies
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
        from backend.app.core.database import SessionLocal
        from backend.app.models.user import UserRole, UserStatus
        from backend.app.schemas.user import UserUpdate
        from backend.app.services.user_service import UserService

        db = SessionLocal()
        user_service = UserService(db)

        # Try to find user by different identifiers
        user = None
        if "@" in identifier:
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
        if kwargs.get("email"):
            update_data["email"] = kwargs["email"]
        if kwargs.get("username"):
            update_data["username"] = kwargs["username"]
        if kwargs.get("first_name"):
            update_data["first_name"] = kwargs["first_name"]
        if kwargs.get("last_name"):
            update_data["last_name"] = kwargs["last_name"]
        if kwargs.get("role"):
            update_data["role"] = UserRole(kwargs["role"])
        if kwargs.get("status"):
            update_data["status"] = UserStatus(kwargs["status"])

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
        for _field, _value in update_data.items():
            pass

    except ImportError as e:
        print_error(f"Backend dependencies not available: {e}")
        print_info("Please run in a backend environment with dependencies installed")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error updating user: {e}")
        sys.exit(1)
    finally:
        if "db" in locals():
            db.close()


def user_delete(identifier, confirm=False):
    """Delete user."""
    if not confirm:
        response = input(
            f"Are you sure you want to delete user {identifier}? This action cannot be undone. (y/N): ",
        )
        if response.lower() != "y":
            return

    try:
        # Import backend dependencies
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
        from backend.app.core.database import SessionLocal
        from backend.app.models.user import UserRole
        from backend.app.services.user_service import UserService

        db = SessionLocal()
        user_service = UserService(db)

        # Try to find user by different identifiers
        user = None
        if "@" in identifier:
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
        if "db" in locals():
            db.close()


def user_reset_password():
    """Reset user password."""
    email = input("User email: ")
    new_password = input("New password: ")

    try:
        # Import backend dependencies
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
        from backend.app.core.database import SessionLocal
        from backend.app.schemas.user import UserPasswordUpdate
        from backend.app.services.user_service import UserService

        db = SessionLocal()
        user_service = UserService(db)

        user = user_service.get_user_by_email(email)
        if not user:
            print_error(f"User not found: {email}")
            sys.exit(1)

        password_data = UserPasswordUpdate(
            current_password="",  # Not needed for admin reset
            new_password=new_password,
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
        if "db" in locals():
            db.close()


def debug_auth_flow():
    """Run authentication flow debug script."""
    script_path = Path(__file__).parent.parent / "scripts" / "debug_auth_flow.js"
    if not script_path.exists():
        print_error(f"Debug script not found: {script_path}")
        return

    print_info("Running authentication flow debug script...")
    print_info(
        "Open browser console and navigate to the application to see debug output"
    )
    print_info(f"Script location: {script_path}")


def debug_frontend_auth():
    """Run frontend authentication debug script."""
    script_path = Path(__file__).parent.parent / "scripts" / "debug_frontend_auth.html"
    if not script_path.exists():
        print_error(f"Debug script not found: {script_path}")
        return

    print_info("Running frontend authentication debug script...")
    print_info(f"Open this file in your browser: {script_path}")
    print_info("This will test localStorage and API calls")


def test_auth_fix():
    """Run authentication fix test script."""
    script_path = Path(__file__).parent.parent / "scripts" / "test_auth_fix.py"
    if not script_path.exists():
        print_error(f"Test script not found: {script_path}")
        return

    print_info("Running authentication fix test...")
    result = subprocess.run(
        [sys.executable, str(script_path)], check=False, cwd=script_path.parent
    )
    if result.returncode == 0:
        print_success("Authentication fix test completed successfully")
    else:
        print_error("Authentication fix test failed")


def test_frontend_auth():
    """Run frontend authentication test script."""
    script_path = Path(__file__).parent.parent / "scripts" / "test_frontend_auth.py"
    if not script_path.exists():
        print_error(f"Test script not found: {script_path}")
        return

    print_info("Running frontend authentication test...")
    result = subprocess.run(
        [sys.executable, str(script_path)], check=False, cwd=script_path.parent
    )
    if result.returncode == 0:
        print_success("Frontend authentication test completed successfully")
    else:
        print_error("Frontend authentication test failed")


def monitoring_containers():
    """Run container monitoring script."""
    script_path = Path(__file__).parent.parent / "scripts" / "monitor_containers.sh"
    if not script_path.exists():
        print_error(f"Monitoring script not found: {script_path}")
        return

    print_info("Starting container monitoring...")
    print_info("Press Ctrl+C to stop monitoring")
    try:
        subprocess.run(["bash", str(script_path)], check=False, cwd=script_path.parent)
    except KeyboardInterrupt:
        print_info("Monitoring stopped by user")


def assistant_list():
    """List all assistants."""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from backend.app.core.config import settings
        from backend.app.models.assistant import Assistant, AssistantStatus
        from backend.app.services.assistant_service import AssistantService

        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        assistant_service = AssistantService(db)

        # Get all assistants (admin view)
        assistants = db.query(Assistant).all()

        if not assistants:
            print_info("No assistants found")
            return

        print_info(f"Found {len(assistants)} assistants:")

        for assistant in assistants:
            status_icon = (
                "✅"
                if assistant.status == AssistantStatus.ACTIVE
                else (
                    "⏸️"
                    if assistant.status == AssistantStatus.INACTIVE
                    else "📝"
                    if assistant.status == AssistantStatus.DRAFT
                    else "🔧"
                )
            )
            public_icon = "🌐" if assistant.is_public else "🔒"

    except Exception as e:
        print_error(f"Error listing assistants: {e}")
        sys.exit(1)
    finally:
        if "db" in locals():
            db.close()


def assistant_show(assistant_id: str):
    """Show detailed information about an assistant."""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from backend.app.core.config import settings
        from backend.app.models.assistant import Assistant
        from backend.app.services.assistant_service import AssistantService

        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        assistant_service = AssistantService(db)

        assistant = db.query(Assistant).filter(Assistant.id == assistant_id).first()

        if not assistant:
            print_error(f"Assistant with ID {assistant_id} not found")
            return

        print_info(f"Assistant Details: {assistant.name}")

        if assistant.tags:
            pass

        if assistant.personality:
            pass

        if assistant.system_prompt:
            pass

        if assistant.instructions:
            pass

    except Exception as e:
        print_error(f"Error showing assistant: {e}")
        sys.exit(1)
    finally:
        if "db" in locals():
            db.close()


def assistant_create():
    """Create a new assistant interactively."""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from backend.app.core.config import settings
        from backend.app.services.assistant_service import AssistantService

        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        assistant_service = AssistantService(db)

        print_info("Creating new assistant...")

        # Get input from user
        name = input("Assistant name: ").strip()
        if not name:
            print_error("Name is required")
            return

        description = input("Description (optional): ").strip() or None
        personality = input("Personality (optional): ").strip() or None
        system_prompt = input("System prompt: ").strip()
        if not system_prompt:
            print_error("System prompt is required")
            return

        instructions = input("Instructions (optional): ").strip() or None
        model = input("Model (default: gpt-4): ").strip() or "gpt-4"
        temperature = input("Temperature (default: 0.7): ").strip() or "0.7"
        max_tokens = input("Max tokens (default: 4096): ").strip() or "4096"
        category = input("Category (optional): ").strip() or None
        is_public = input("Public (y/N): ").strip().lower() == "y"

        # Create assistant data object
        class AssistantCreate:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        assistant_data = AssistantCreate(
            name=name,
            description=description,
            personality=personality,
            system_prompt=system_prompt,
            instructions=instructions,
            model=model,
            temperature=float(temperature),
            max_tokens=int(max_tokens),
            category=category,
            is_public=is_public,
            tags=[],
            tools_config=[],
        )

        # Create assistant (using admin user ID)
        admin_user_id = "00000000-0000-0000-0000-000000000000"  # Placeholder admin ID
        assistant = assistant_service.create_assistant(assistant_data, admin_user_id)

        print_success(
            f"Assistant '{assistant.name}' created successfully with ID: {assistant.id}"
        )

    except Exception as e:
        print_error(f"Error creating assistant: {e}")
        sys.exit(1)
    finally:
        if "db" in locals():
            db.close()


def assistant_delete(assistant_id: str, confirm: bool = False):
    """Delete an assistant."""
    if not confirm:
        response = input(
            f"⚠️  WARNING: This will delete assistant {assistant_id}. Are you sure? (yes/no): "
        )
        if response.lower() != "yes":
            print_info("Deletion cancelled")
            return

    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from backend.app.core.config import settings
        from backend.app.models.assistant import Assistant
        from backend.app.services.assistant_service import AssistantService

        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        assistant_service = AssistantService(db)

        # Get assistant name for confirmation
        assistant = db.query(Assistant).filter(Assistant.id == assistant_id).first()
        if not assistant:
            print_error(f"Assistant with ID {assistant_id} not found")
            return

        # Delete assistant (using admin user ID)
        admin_user_id = "00000000-0000-0000-0000-000000000000"  # Placeholder admin ID
        success = assistant_service.delete_assistant(assistant_id, admin_user_id)

        if success:
            print_success(f"Assistant '{assistant.name}' deleted successfully")
        else:
            print_error("Failed to delete assistant")

    except Exception as e:
        print_error(f"Error deleting assistant: {e}")
        sys.exit(1)
    finally:
        if "db" in locals():
            db.close()


def assistant_activate(assistant_id: str):
    """Activate an assistant."""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from backend.app.core.config import settings
        from backend.app.models.assistant import Assistant
        from backend.app.services.assistant_service import AssistantService

        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        assistant_service = AssistantService(db)

        # Get assistant name for confirmation
        assistant = db.query(Assistant).filter(Assistant.id == assistant_id).first()
        if not assistant:
            print_error(f"Assistant with ID {assistant_id} not found")
            return

        # Activate assistant (using admin user ID)
        admin_user_id = "00000000-0000-0000-0000-000000000000"  # Placeholder admin ID
        updated_assistant = assistant_service.activate_assistant(
            assistant_id, admin_user_id
        )

        if updated_assistant:
            print_success(f"Assistant '{assistant.name}' activated successfully")
        else:
            print_error("Failed to activate assistant")

    except Exception as e:
        print_error(f"Error activating assistant: {e}")
        sys.exit(1)
    finally:
        if "db" in locals():
            db.close()


def assistant_deactivate(assistant_id: str):
    """Deactivate an assistant."""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from backend.app.core.config import settings
        from backend.app.models.assistant import Assistant
        from backend.app.services.assistant_service import AssistantService

        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        assistant_service = AssistantService(db)

        # Get assistant name for confirmation
        assistant = db.query(Assistant).filter(Assistant.id == assistant_id).first()
        if not assistant:
            print_error(f"Assistant with ID {assistant_id} not found")
            return

        # Deactivate assistant (using admin user ID)
        admin_user_id = "00000000-0000-0000-0000-000000000000"  # Placeholder admin ID
        updated_assistant = assistant_service.deactivate_assistant(
            assistant_id, admin_user_id
        )

        if updated_assistant:
            print_success(f"Assistant '{assistant.name}' deactivated successfully")
        else:
            print_error("Failed to deactivate assistant")

    except Exception as e:
        print_error(f"Error deactivating assistant: {e}")
        sys.exit(1)
    finally:
        if "db" in locals():
            db.close()


def show_help():
    """Show help message."""


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="ConvoSphere Admin CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Database commands
    db_parser = subparsers.add_parser("db", help="Database management")
    db_subparsers = db_parser.add_subparsers(dest="db_command")
    db_subparsers.add_parser("migrate", help="Run migrations")
    db_subparsers.add_parser("status", help="Show migration status")
    db_subparsers.add_parser("test-connection", help="Test database connection")
    db_subparsers.add_parser("info", help="Show database information")
    db_subparsers.add_parser(
        "reset", help="Completely reset database (drop all tables and recreate)"
    )
    db_subparsers.add_parser(
        "clear-data", help="Clear all data but keep table structure"
    )

    downgrade_parser = db_subparsers.add_parser(
        "downgrade",
        help="Downgrade to revision",
    )
    downgrade_parser.add_argument("revision", help="Revision to downgrade to")

    # User commands
    user_parser = subparsers.add_parser("user", help="User management")
    user_subparsers = user_parser.add_subparsers(dest="user_command")
    user_subparsers.add_parser("create-admin", help="Create admin user interactively")
    user_subparsers.add_parser("create-secure", help="Create user from environment variables")
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
    update_parser.add_argument(
        "--role",
        choices=["user", "admin", "super_admin"],
        help="User role",
    )
    update_parser.add_argument(
        "--status",
        choices=["active", "inactive", "suspended"],
        help="User status",
    )

    # User delete command
    delete_parser = user_subparsers.add_parser("delete", help="Delete user")
    delete_parser.add_argument("identifier", help="User email, username, or ID")
    delete_parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation",
    )

    # User create command
    create_parser = user_subparsers.add_parser("create", help="Create new user")
    create_parser.add_argument("--email", required=True, help="User email")
    create_parser.add_argument("--username", required=True, help="Username")
    create_parser.add_argument("--password", required=True, help="Password")
    create_parser.add_argument("--first-name", help="First name")
    create_parser.add_argument("--last-name", help="Last name")
    create_parser.add_argument(
        "--role",
        choices=["user", "admin", "super_admin"],
        default="user",
        help="User role",
    )
    create_parser.add_argument(
        "--status",
        choices=["active", "inactive", "suspended"],
        default="active",
        help="User status",
    )

    # Backup commands
    backup_parser = subparsers.add_parser("backup", help="Backup and recovery")
    backup_subparsers = backup_parser.add_subparsers(dest="backup_command")

    create_parser = backup_subparsers.add_parser("create", help="Create backup")
    create_parser.add_argument("--output", help="Output file path")

    restore_parser = backup_subparsers.add_parser("restore", help="Restore from backup")
    restore_parser.add_argument("backup_file", help="Backup file to restore")
    restore_parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation",
    )

    list_parser = backup_subparsers.add_parser("list", help="List backups")
    list_parser.add_argument("--backup-dir", default=".", help="Backup directory")

    # Monitoring commands
    monitoring_parser = subparsers.add_parser("monitoring", help="System monitoring")
    monitoring_subparsers = monitoring_parser.add_subparsers(dest="monitoring_command")
    monitoring_subparsers.add_parser("health", help="Check system health")
    monitoring_subparsers.add_parser("containers", help="Monitor containers")

    logs_parser = monitoring_subparsers.add_parser("logs", help="Show logs")
    logs_parser.add_argument("--lines", type=int, default=50, help="Number of lines")
    logs_parser.add_argument("--level", default="INFO", help="Log level")

    # Config commands
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_subparsers = config_parser.add_subparsers(dest="config_command")
    config_subparsers.add_parser("show", help="Show configuration")
    config_subparsers.add_parser("validate", help="Validate configuration")

    # Dev commands
    dev_parser = subparsers.add_parser("dev", help="Development tools")
    dev_subparsers = dev_parser.add_subparsers(dest="dev_command")

    test_data_parser = dev_subparsers.add_parser("test-data", help="Create test data")
    test_data_parser.add_argument(
        "--users",
        type=int,
        default=5,
        help="Number of users",
    )

    dev_subparsers.add_parser("quality-check", help="Run code quality checks")

    api_test_parser = dev_subparsers.add_parser("api-test", help="Run API tests")
    api_test_parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="API URL",
    )

    # Debug commands
    debug_parser = subparsers.add_parser("debug", help="Debugging tools")
    debug_subparsers = debug_parser.add_subparsers(dest="debug_command")
    debug_subparsers.add_parser("auth-flow", help="Debug authentication flow")
    debug_subparsers.add_parser("frontend-auth", help="Debug frontend authentication")
    debug_subparsers.add_parser("test-auth-fix", help="Test authentication fix")
    debug_subparsers.add_parser(
        "test-frontend-auth", help="Test frontend authentication"
    )

    # Assistant commands
    assistant_parser = subparsers.add_parser("assistant", help="Assistant management")
    assistant_subparsers = assistant_parser.add_subparsers(dest="assistant_command")
    assistant_subparsers.add_parser("list", help="List all assistants")
    assistant_subparsers.add_parser("create", help="Create a new assistant")

    show_parser = assistant_subparsers.add_parser("show", help="Show assistant details")
    show_parser.add_argument("assistant_id", help="Assistant ID")

    delete_parser = assistant_subparsers.add_parser(
        "delete", help="Delete an assistant"
    )
    delete_parser.add_argument("assistant_id", help="Assistant ID")
    delete_parser.add_argument(
        "--confirm", action="store_true", help="Skip confirmation"
    )

    activate_parser = assistant_subparsers.add_parser(
        "activate", help="Activate an assistant"
    )
    activate_parser.add_argument("assistant_id", help="Assistant ID")

    deactivate_parser = assistant_subparsers.add_parser(
        "deactivate", help="Deactivate an assistant"
    )
    deactivate_parser.add_argument("assistant_id", help="Assistant ID")

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
        elif args.db_command == "test-connection":
            db_test_connection()
        elif args.db_command == "info":
            db_info()
        elif args.db_command == "reset":
            db_reset()
        elif args.db_command == "clear-data":
            db_clear_data()

    elif args.command == "user":
        if args.user_command == "create-admin":
            user_create_admin()
        elif args.user_command == "create-secure":
            user_create_secure()
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
                status=args.status,
            )
        elif args.user_command == "update":
            update_data = {}
            if args.email:
                update_data["email"] = args.email
            if args.username:
                update_data["username"] = args.username
            if args.first_name:
                update_data["first_name"] = args.first_name
            if args.last_name:
                update_data["last_name"] = args.last_name
            if args.role:
                update_data["role"] = args.role
            if args.status:
                update_data["status"] = args.status
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
        elif args.monitoring_command == "containers":
            monitoring_containers()
        elif args.monitoring_command == "logs":
            monitoring_logs(args.lines, args.level)

    elif args.command == "config":
        if args.config_command == "show":
            config_show()
        elif args.config_command == "validate":
            config_validate()

    elif args.command == "dev":
        if args.dev_command == "test-data":
            dev_test_data(args.users)
        elif args.dev_command == "quality-check":
            dev_quality_check()
        elif args.dev_command == "api-test":
            dev_api_test(args.url)

    elif args.command == "debug":
        if args.debug_command == "auth-flow":
            debug_auth_flow()
        elif args.debug_command == "frontend-auth":
            debug_frontend_auth()
        elif args.debug_command == "test-auth-fix":
            test_auth_fix()
        elif args.debug_command == "test-frontend-auth":
            test_frontend_auth()

    elif args.command == "assistant":
        if args.assistant_command == "list":
            assistant_list()
        elif args.assistant_command == "create":
            assistant_create()
        elif args.assistant_command == "show":
            assistant_show(args.assistant_id)
        elif args.assistant_command == "delete":
            assistant_delete(args.assistant_id, args.confirm)
        elif args.assistant_command == "activate":
            assistant_activate(args.assistant_id)
        elif args.assistant_command == "deactivate":
            assistant_deactivate(args.assistant_id)


if __name__ == "__main__":
    main()
