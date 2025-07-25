#!/usr/bin/env python3
import argparse
import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.core.database import SessionLocal as AppSessionLocal
from app.core.redis_client import get_redis
from app.core.weaviate_client import get_weaviate
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

# Dynamisch Backend-App importieren
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
from app.core.config import settings
from app.models.user import UserRole, UserStatus
from app.schemas.user import UserCreate
from app.services.user_service import UserService

# DB-Session vorbereiten
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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


def db_downgrade(revision):
    """Downgrade DB to a specific revision."""
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


def db_status():
    """Show Alembic migration status."""
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


def db_test_connection():
    """Test database connection."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print_success("Database connection successful")
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        sys.exit(1)


def db_info():
    """Show database information."""
    try:
        with engine.connect() as conn:
            # Get database name
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"Database: {db_name}")
            
            # Get table count
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            table_count = result.scalar()
            print(f"Tables: {table_count}")
            
            # Get user count
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            print(f"Users: {user_count}")
            
    except Exception as e:
        print_error(f"Error getting database info: {e}")
        sys.exit(1)


def user_create_admin():
    """Create an initial admin user."""
    print("Creating admin user...")
    email = input("Email: ")
    username = input("Username: ")
    password = input("Password: ")
    first_name = input("First name (optional): ") or None
    last_name = input("Last name (optional): ") or None
    
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
    try:
        user = user_service.create_user(user_data)
        print_success(f"Admin user created: {user.email} ({user.id})")
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)
    finally:
        db.close()


def user_list():
    """List all users (id, email, username, role, status)."""
    db = SessionLocal()
    user_service = UserService(db)
    try:
        # Dummy current_user mit Super-Admin-Rechten für vollständige Liste
        from app.models.user import UserRole

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
        for user in users:
            print(f"{user.id} | {user.email} | {user.username} | {user.role} | {user.status}")
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)
    finally:
        db.close()


def user_reset_password():
    """Reset user password."""
    email = input("User email: ")
    new_password = input("New password: ")
    
    db = SessionLocal()
    user_service = UserService(db)
    try:
        user = user_service.get_user_by_email(email)
        if not user:
            print_error(f"User not found: {email}")
            sys.exit(1)
        
        user_service.update_user_password(user.id, new_password)
        print_success(f"Password reset for user: {email}")
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)
    finally:
        db.close()


def backup_create(output=None):
    """Create database backup."""
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"backup_{timestamp}.sql"
    
    try:
        # Extract database connection info
        db_url = settings.SQLALCHEMY_DATABASE_URI
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
            shutil.copy2(db_url.replace("sqlite:///", ""), output)
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
        db_url = settings.SQLALCHEMY_DATABASE_URI
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
    
    # Database health
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database: OK")
    except Exception as e:
        print(f"❌ Database: ERROR - {e}")
    
    # Redis health
    try:
        redis_client = get_redis_client()
        redis_client.ping()
        print("✅ Redis: OK")
    except Exception as e:
        print(f"❌ Redis: ERROR - {e}")
    
    # Weaviate health
    try:
        weaviate_client = get_weaviate_client()
        weaviate_client.is_ready()
        print("✅ Weaviate: OK")
    except Exception as e:
        print(f"❌ Weaviate: ERROR - {e}")
    
    # Backend API health
    try:
        import requests
        response = requests.get(f"{settings.backend_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API: OK")
        else:
            print(f"❌ Backend API: ERROR - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Backend API: ERROR - {e}")


def monitoring_logs(lines=50, level="INFO"):
    """Show recent application logs."""
    log_file = settings.log_file
    if not os.path.exists(log_file):
        print_error(f"Log file not found: {log_file}")
        return
    
    try:
        with open(log_file, 'r') as f:
            log_lines = f.readlines()
        
        # Filter by level and get last N lines
        filtered_lines = [line for line in log_lines if level in line]
        recent_lines = filtered_lines[-lines:] if len(filtered_lines) > lines else filtered_lines
        
        for line in recent_lines:
            print(line.rstrip())
            
    except Exception as e:
        print_error(f"Error reading logs: {e}")


def config_show():
    """Show current configuration."""
    print("📋 Current Configuration:")
    print(f"Environment: {settings.environment}")
    print(f"Debug: {settings.debug}")
    print(f"Database: {settings.database_url}")
    print(f"Redis: {settings.redis_url}")
    print(f"Weaviate: {settings.weaviate_url}")
    print(f"Backend URL: {settings.backend_url}")
    print(f"Upload Directory: {settings.upload_dir}")
    print(f"Log Level: {settings.log_level}")


def config_validate():
    """Validate configuration."""
    print("🔍 Validating configuration...")
    
    errors = []
    
    # Check required settings
    if not settings.secret_key or len(settings.secret_key) < 32:
        errors.append("Secret key must be at least 32 characters long")
    
    if not settings.database_url:
        errors.append("Database URL is required")
    
    if not settings.redis_url:
        errors.append("Redis URL is required")
    
    # Check file paths
    if not os.path.exists(settings.upload_dir):
        errors.append(f"Upload directory does not exist: {settings.upload_dir}")
    
    # Check API keys (optional but recommended)
    if not settings.openai_api_key and not settings.anthropic_api_key:
        errors.append("Warning: No AI provider API key configured")
    
    if errors:
        print_error("Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print_success("Configuration is valid")


def dev_test_data(users=5):
    """Create test data for development."""
    db = SessionLocal()
    user_service = UserService(db)
    
    try:
        print(f"Creating {users} test users...")
        
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
            user = user_service.create_user(user_data)
            print(f"Created user: {user.email}")
        
        print_success("Test data created successfully")
        
    except Exception as e:
        print_error(f"Error creating test data: {e}")
        sys.exit(1)
    finally:
        db.close()


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
            
    except Exception as e:
        print_error(f"API test failed: {e}")


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
    print("  db test-connection      Test database connection")
    print("  db info                 Show database information")
    print()
    print("User Management:")
    print("  user create-admin       Create admin user")
    print("  user list               List all users")
    print("  user reset-password     Reset user password")
    print()
    print("Backup & Recovery:")
    print("  backup create           Create database backup")
    print("  backup restore <file>   Restore from backup")
    print("  backup list             List available backups")
    print()
    print("Monitoring:")
    print("  monitoring health       Check system health")
    print("  monitoring logs         Show application logs")
    print()
    print("Configuration:")
    print("  config show             Show current configuration")
    print("  config validate         Validate configuration")
    print()
    print("Development:")
    print("  dev test-data           Create test data")
    print("  dev quality-check       Run code quality checks")
    print("  dev api-test            Run API tests")
    print()
    print("Examples:")
    print("  python admin.py db migrate")
    print("  python admin.py user create-admin")
    print("  python admin.py backup create")
    print("  python admin.py monitoring health")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="ChatAssistant Admin CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Database commands
    db_parser = subparsers.add_parser("db", help="Database management")
    db_subparsers = db_parser.add_subparsers(dest="db_command")
    db_subparsers.add_parser("migrate", help="Run migrations")
    db_subparsers.add_parser("status", help="Show migration status")
    db_subparsers.add_parser("test-connection", help="Test database connection")
    db_subparsers.add_parser("info", help="Show database information")
    
    downgrade_parser = db_subparsers.add_parser("downgrade", help="Downgrade to revision")
    downgrade_parser.add_argument("revision", help="Revision to downgrade to")
    
    # User commands
    user_parser = subparsers.add_parser("user", help="User management")
    user_subparsers = user_parser.add_subparsers(dest="user_command")
    user_subparsers.add_parser("create-admin", help="Create admin user")
    user_subparsers.add_parser("list", help="List all users")
    user_subparsers.add_parser("reset-password", help="Reset user password")
    
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
    test_data_parser.add_argument("--users", type=int, default=5, help="Number of users")
    
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
        elif args.db_command == "test-connection":
            db_test_connection()
        elif args.db_command == "info":
            db_info()
    
    elif args.command == "user":
        if args.user_command == "create-admin":
            user_create_admin()
        elif args.user_command == "list":
            user_list()
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


if __name__ == "__main__":
    main()
