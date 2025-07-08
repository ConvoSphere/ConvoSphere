#!/usr/bin/env python3
"""
ConvoSphere CLI Management Tool
Provides comprehensive administration capabilities for the ConvoSphere platform.

Usage:
    python scripts/convosphere.py [COMMAND] [OPTIONS]

Examples:
    python scripts/convosphere.py users list
    python scripts/convosphere.py database backup --file backup.sql
    python scripts/convosphere.py services status
    python scripts/convosphere.py deploy --environment prod
"""

import os
import sys
import typer
import click
import yaml
import json
import subprocess
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import docker
from docker.errors import DockerException

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

app = typer.Typer(
    name="convosphere",
    help="ConvoSphere CLI Management Tool",
    add_completion=False
)

# Configuration
CONFIG_FILE = project_root / "config" / "cli.yaml"
DOCKER_COMPOSE_FILE = project_root / "docker-compose.yml"
ENV_FILE = project_root / ".env"

def load_config():
    """Load CLI configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f)
    return {}

def get_database_connection():
    """Get database connection from environment."""
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "convosphere"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "password")
        )
    except Exception as e:
        typer.echo(f"❌ Database connection failed: {e}")
        raise typer.Exit(1)

def get_docker_client():
    """Get Docker client."""
    try:
        return docker.from_env()
    except DockerException as e:
        typer.echo(f"❌ Docker connection failed: {e}")
        raise typer.Exit(1)

@app.command()
def users(
    action: str = typer.Argument(..., help="Action: list, create, update, delete, reset-password"),
    email: Optional[str] = typer.Option(None, help="User email"),
    role: Optional[str] = typer.Option(None, help="User role (admin, user, moderator)"),
    password: Optional[str] = typer.Option(None, help="User password"),
    user_id: Optional[str] = typer.Option(None, help="User ID for update/delete operations")
):
    """Manage users in the system."""
    conn = get_database_connection()
    
    try:
        if action == "list":
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, email, username, is_active, created_at, updated_at
                    FROM users ORDER BY created_at DESC
                """)
                users = cur.fetchall()
                
                if not users:
                    typer.echo("No users found.")
                    return
                
                typer.echo("\n📋 Users:")
                typer.echo("-" * 80)
                for user in users:
                    status = "✅ Active" if user['is_active'] else "❌ Inactive"
                    typer.echo(f"ID: {user['id']} | Email: {user['email']} | Status: {status}")
                    typer.echo(f"Created: {user['created_at']}")
                    typer.echo("-" * 40)
        
        elif action == "create":
            if not email or not password:
                typer.echo("❌ Email and password are required for user creation")
                raise typer.Exit(1)
            
            from app.core.security import get_password_hash
            hashed_password = get_password_hash(password)
            
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO users (email, username, hashed_password, is_active, role)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (email, email.split('@')[0], hashed_password, True, role or 'user'))
                user_id = cur.fetchone()[0]
                conn.commit()
                typer.echo(f"✅ User created with ID: {user_id}")
        
        elif action == "update":
            if not user_id:
                typer.echo("❌ User ID is required for update")
                raise typer.Exit(1)
            
            updates = []
            values = []
            
            if email:
                updates.append("email = %s")
                values.append(email)
            if role:
                updates.append("role = %s")
                values.append(role)
            if password:
                from app.core.security import get_password_hash
                updates.append("hashed_password = %s")
                values.append(get_password_hash(password))
            
            if not updates:
                typer.echo("❌ No fields to update")
                raise typer.Exit(1)
            
            values.append(user_id)
            with conn.cursor() as cur:
                cur.execute(f"""
                    UPDATE users SET {', '.join(updates)}, updated_at = NOW()
                    WHERE id = %s
                """, values)
                conn.commit()
                typer.echo(f"✅ User {user_id} updated successfully")
        
        elif action == "delete":
            if not user_id:
                typer.echo("❌ User ID is required for deletion")
                raise typer.Exit(1)
            
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
                conn.commit()
                typer.echo(f"✅ User {user_id} deleted successfully")
        
        elif action == "reset-password":
            if not user_id or not password:
                typer.echo("❌ User ID and password are required for password reset")
                raise typer.Exit(1)
            
            from app.core.security import get_password_hash
            hashed_password = get_password_hash(password)
            
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE users SET hashed_password = %s, updated_at = NOW()
                    WHERE id = %s
                """, (hashed_password, user_id))
                conn.commit()
                typer.echo(f"✅ Password reset for user {user_id}")
        
        else:
            typer.echo(f"❌ Unknown action: {action}")
            raise typer.Exit(1)
    
    finally:
        conn.close()

@app.command()
def database(
    action: str = typer.Argument(..., help="Action: status, migrate, backup, restore, reset"),
    file: Optional[Path] = typer.Option(None, help="Backup/restore file path"),
    force: bool = typer.Option(False, help="Force operation without confirmation")
):
    """Manage database operations."""
    
    if action == "status":
        conn = get_database_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()[0]
                typer.echo(f"✅ Database connected: {version}")
                
                cur.execute("SELECT COUNT(*) FROM users")
                user_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM conversations")
                conv_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM assistants")
                assistant_count = cur.fetchone()[0]
                
                typer.echo(f"📊 Statistics:")
                typer.echo(f"  Users: {user_count}")
                typer.echo(f"  Conversations: {conv_count}")
                typer.echo(f"  Assistants: {assistant_count}")
        finally:
            conn.close()
    
    elif action == "migrate":
        typer.echo("🔄 Running database migrations...")
        try:
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                cwd=project_root / "backend",
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                typer.echo("✅ Migrations completed successfully")
            else:
                typer.echo(f"❌ Migration failed: {result.stderr}")
                raise typer.Exit(1)
        except FileNotFoundError:
            typer.echo("❌ Alembic not found. Please install it first.")
            raise typer.Exit(1)
    
    elif action == "backup":
        if not file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file = project_root / f"backup_{timestamp}.sql"
        
        typer.echo(f"💾 Creating backup: {file}")
        try:
            result = subprocess.run([
                "pg_dump",
                "-h", os.getenv("DB_HOST", "localhost"),
                "-p", os.getenv("DB_PORT", "5432"),
                "-U", os.getenv("DB_USER", "postgres"),
                "-d", os.getenv("DB_NAME", "convosphere"),
                "-f", str(file)
            ], env={**os.environ, "PGPASSWORD": os.getenv("DB_PASSWORD", "password")})
            
            if result.returncode == 0:
                typer.echo(f"✅ Backup created: {file}")
            else:
                typer.echo("❌ Backup failed")
                raise typer.Exit(1)
        except FileNotFoundError:
            typer.echo("❌ pg_dump not found. Please install PostgreSQL client tools.")
            raise typer.Exit(1)
    
    elif action == "restore":
        if not file or not file.exists():
            typer.echo("❌ Backup file not found")
            raise typer.Exit(1)
        
        if not force:
            confirm = typer.confirm("⚠️  This will overwrite the current database. Continue?")
            if not confirm:
                typer.echo("Operation cancelled.")
                return
        
        typer.echo(f"🔄 Restoring from backup: {file}")
        try:
            result = subprocess.run([
                "psql",
                "-h", os.getenv("DB_HOST", "localhost"),
                "-p", os.getenv("DB_PORT", "5432"),
                "-U", os.getenv("DB_USER", "postgres"),
                "-d", os.getenv("DB_NAME", "convosphere"),
                "-f", str(file)
            ], env={**os.environ, "PGPASSWORD": os.getenv("DB_PASSWORD", "password")})
            
            if result.returncode == 0:
                typer.echo("✅ Database restored successfully")
            else:
                typer.echo("❌ Restore failed")
                raise typer.Exit(1)
        except FileNotFoundError:
            typer.echo("❌ psql not found. Please install PostgreSQL client tools.")
            raise typer.Exit(1)
    
    elif action == "reset":
        if not force:
            confirm = typer.confirm("⚠️  This will delete ALL data. Are you sure?")
            if not confirm:
                typer.echo("Operation cancelled.")
                return
        
        typer.echo("🔄 Resetting database...")
        conn = get_database_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA public CASCADE")
                cur.execute("CREATE SCHEMA public")
                conn.commit()
            typer.echo("✅ Database reset successfully")
        finally:
            conn.close()
    
    else:
        typer.echo(f"❌ Unknown action: {action}")
        raise typer.Exit(1)

@app.command()
def services(
    action: str = typer.Argument(..., help="Action: status, start, stop, restart, logs"),
    service: Optional[str] = typer.Option(None, help="Service name (backend, frontend, postgres, redis, weaviate)"),
    tail: int = typer.Option(50, help="Number of log lines to show")
):
    """Manage system services."""
    
    if not DOCKER_COMPOSE_FILE.exists():
        typer.echo("❌ docker-compose.yml not found")
        raise typer.Exit(1)
    
    if action == "status":
        try:
            result = subprocess.run(
                ["docker-compose", "ps"],
                cwd=project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                typer.echo("📊 Service Status:")
                typer.echo(result.stdout)
            else:
                typer.echo("❌ Failed to get service status")
                raise typer.Exit(1)
        except FileNotFoundError:
            typer.echo("❌ docker-compose not found")
            raise typer.Exit(1)
    
    elif action in ["start", "stop", "restart"]:
        services = [service] if service else []
        try:
            cmd = ["docker-compose", action] + services
            result = subprocess.run(cmd, cwd=project_root)
            if result.returncode == 0:
                typer.echo(f"✅ Services {action}ed successfully")
            else:
                typer.echo(f"❌ Failed to {action} services")
                raise typer.Exit(1)
        except FileNotFoundError:
            typer.echo("❌ docker-compose not found")
            raise typer.Exit(1)
    
    elif action == "logs":
        services = [service] if service else []
        try:
            cmd = ["docker-compose", "logs", "--tail", str(tail)] + services
            result = subprocess.run(cmd, cwd=project_root)
            if result.returncode != 0:
                typer.echo("❌ Failed to get logs")
                raise typer.Exit(1)
        except FileNotFoundError:
            typer.echo("❌ docker-compose not found")
            raise typer.Exit(1)
    
    else:
        typer.echo(f"❌ Unknown action: {action}")
        raise typer.Exit(1)

@app.command()
def deploy(
    environment: str = typer.Argument(..., help="Environment: dev, staging, prod"),
    force: bool = typer.Option(False, help="Force deployment without confirmation"),
    build: bool = typer.Option(True, help="Build images before deployment")
):
    """Deploy the application."""
    
    if environment not in ["dev", "staging", "prod"]:
        typer.echo("❌ Invalid environment. Use: dev, staging, prod")
        raise typer.Exit(1)
    
    if not force:
        confirm = typer.confirm(f"🚀 Deploy to {environment} environment?")
        if not confirm:
            typer.echo("Deployment cancelled.")
            return
    
    typer.echo(f"🚀 Deploying to {environment}...")
    
    try:
        # Build images if requested
        if build:
            typer.echo("🔨 Building images...")
            result = subprocess.run(
                ["docker-compose", "build"],
                cwd=project_root
            )
            if result.returncode != 0:
                typer.echo("❌ Build failed")
                raise typer.Exit(1)
        
        # Deploy
        typer.echo("📦 Deploying services...")
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd=project_root
        )
        if result.returncode == 0:
            typer.echo(f"✅ Deployment to {environment} completed successfully")
        else:
            typer.echo("❌ Deployment failed")
            raise typer.Exit(1)
    
    except FileNotFoundError:
        typer.echo("❌ docker-compose not found")
        raise typer.Exit(1)

@app.command()
def health(
    detailed: bool = typer.Option(False, help="Show detailed health information")
):
    """Check system health."""
    
    typer.echo("🏥 Checking system health...")
    
    # Database health
    try:
        conn = get_database_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        conn.close()
        typer.echo("✅ Database: Healthy")
    except Exception as e:
        typer.echo(f"❌ Database: Unhealthy - {e}")
    
    # Docker services health
    try:
        client = get_docker_client()
        containers = client.containers.list()
        typer.echo(f"✅ Docker: {len(containers)} containers running")
        
        if detailed:
            for container in containers:
                status = container.status
                health = "Healthy" if container.attrs.get('State', {}).get('Health', {}).get('Status') == 'healthy' else "Unknown"
                typer.echo(f"  {container.name}: {status} ({health})")
    
    except Exception as e:
        typer.echo(f"❌ Docker: Unhealthy - {e}")
    
    # API health
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            typer.echo("✅ API: Healthy")
            if detailed:
                health_data = response.json()
                typer.echo(f"  Status: {health_data.get('status', 'unknown')}")
        else:
            typer.echo(f"❌ API: Unhealthy - Status {response.status_code}")
    except Exception as e:
        typer.echo(f"❌ API: Unhealthy - {e}")

@app.command()
def config(
    action: str = typer.Argument(..., help="Action: show, set, get, reset"),
    key: Optional[str] = typer.Option(None, help="Configuration key"),
    value: Optional[str] = typer.Option(None, help="Configuration value")
):
    """Manage configuration."""
    
    if action == "show":
        typer.echo("📋 Current Configuration:")
        if ENV_FILE.exists():
            with open(ENV_FILE, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        typer.echo(f"  {line.strip()}")
        else:
            typer.echo("  No .env file found")
    
    elif action == "set":
        if not key or not value:
            typer.echo("❌ Key and value are required")
            raise typer.Exit(1)
        
        # Read current env file
        env_lines = []
        if ENV_FILE.exists():
            with open(ENV_FILE, 'r') as f:
                env_lines = f.readlines()
        
        # Update or add the key
        found = False
        for i, line in enumerate(env_lines):
            if line.startswith(f"{key}="):
                env_lines[i] = f"{key}={value}\n"
                found = True
                break
        
        if not found:
            env_lines.append(f"{key}={value}\n")
        
        # Write back
        ENV_FILE.parent.mkdir(exist_ok=True)
        with open(ENV_FILE, 'w') as f:
            f.writelines(env_lines)
        
        typer.echo(f"✅ Set {key}={value}")
    
    elif action == "get":
        if not key:
            typer.echo("❌ Key is required")
            raise typer.Exit(1)
        
        value = os.getenv(key)
        if value:
            typer.echo(f"{key}={value}")
        else:
            typer.echo(f"❌ Key '{key}' not found")
            raise typer.Exit(1)
    
    elif action == "reset":
        if ENV_FILE.exists():
            backup_file = ENV_FILE.with_suffix('.env.backup')
            ENV_FILE.rename(backup_file)
            typer.echo(f"✅ Configuration reset. Backup saved to {backup_file}")
        else:
            typer.echo("✅ No configuration file to reset")
    
    else:
        typer.echo(f"❌ Unknown action: {action}")
        raise typer.Exit(1)

@app.command()
def logs(
    service: Optional[str] = typer.Option(None, help="Service name"),
    tail: int = typer.Option(100, help="Number of lines to show"),
    follow: bool = typer.Option(False, help="Follow log output")
):
    """Show application logs."""
    
    cmd = ["docker-compose", "logs"]
    
    if follow:
        cmd.append("-f")
    
    cmd.extend(["--tail", str(tail)])
    
    if service:
        cmd.append(service)
    
    try:
        subprocess.run(cmd, cwd=project_root)
    except FileNotFoundError:
        typer.echo("❌ docker-compose not found")
        raise typer.Exit(1)

if __name__ == "__main__":
    app() 