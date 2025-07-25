#!/usr/bin/env python3
import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

import click
from app.core.database import SessionLocal as AppSessionLocal
from app.core.redis_client import get_redis_client
from app.core.weaviate_client import get_weaviate_client
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

# Dynamisch Backend-App importieren
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
from app.core.config import settings
from app.models.user import UserRole, UserStatus
from app.schemas.user import UserCreate
from app.services.user_service import UserService

# DB-Session vorbereiten
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@click.group()
def cli():
    """Admin CLI for ChatAssistant platform."""


@cli.group()
def db():
    """Database management commands."""


@db.command("migrate")
def migrate():
    """Run Alembic migrations (upgrade head)."""
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        check=False,
        cwd=os.path.dirname(__file__),
        capture_output=True,
        text=True,
    )
    click.echo(result.stdout)
    if result.returncode != 0:
        click.echo(result.stderr)
        sys.exit(result.returncode)


@db.command("downgrade")
@click.argument("revision")
def downgrade(revision):
    """Downgrade DB to a specific revision."""
    result = subprocess.run(
        ["alembic", "downgrade", revision],
        check=False,
        cwd=os.path.dirname(__file__),
        capture_output=True,
        text=True,
    )
    click.echo(result.stdout)
    if result.returncode != 0:
        click.echo(result.stderr)
        sys.exit(result.returncode)


@db.command("status")
def status():
    """Show Alembic migration status."""
    result = subprocess.run(
        ["alembic", "current"],
        check=False,
        cwd=os.path.dirname(__file__),
        capture_output=True,
        text=True,
    )
    click.echo(result.stdout)
    if result.returncode != 0:
        click.echo(result.stderr)
        sys.exit(result.returncode)


@cli.group()
def user():
    """User management commands."""


@user.command("create-admin")
@click.option("--email", prompt=True, help="Admin email")
@click.option("--username", prompt=True, help="Admin username")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="Admin password",
)
@click.option("--first-name", default=None, help="First name")
@click.option("--last-name", default=None, help="Last name")
def create_admin(email, username, password, first_name, last_name):
    """Create an initial admin user."""
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
        click.echo(f"✅ Admin user created: {user.email} ({user.id})")
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        db.close()


@user.command("list")
def list_users():
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
            click.echo(
                f"{user.id} | {user.email} | {user.username} | {user.role} | {user.status}",
            )
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        db.close()


@cli.group()
def scripts():
    """Run utility scripts from the scripts/ folder."""


@scripts.command("run")
@click.argument("script")
@click.argument("args", nargs=-1)
def run_script(script, args):
    """Run a script from scripts/ (e.g. validate_translations.py)."""
    script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", script)
    if not os.path.isfile(script_path):
        click.echo(f"❌ Script not found: {script_path}")
        sys.exit(1)
    result = subprocess.run(
        [sys.executable, script_path, *args],
        check=False,
        capture_output=True,
        text=True,
    )
    click.echo(result.stdout)
    if result.returncode != 0:
        click.echo(result.stderr)
        sys.exit(result.returncode)


@cli.group()
def health():
    """System health check commands."""


@health.command("check")
def health_check():
    """Check DB, Redis, Weaviate connectivity."""
    # DB
    db_ok = False
    try:
        db = AppSessionLocal()
        db.execute("SELECT 1")
        db_ok = True
    except OperationalError:
        db_ok = False
    finally:
        db.close()
    click.echo(f"DB:     {'✅' if db_ok else '❌'}")
    # Redis
    try:
        redis = get_redis_client()
        redis.ping()
        click.echo("Redis:  ✅")
    except Exception:
        click.echo("Redis:  ❌")
    # Weaviate
    try:
        weaviate = get_weaviate_client()
        if hasattr(weaviate, "is_ready") and weaviate.is_ready():
            click.echo("Weaviate: ✅")
        else:
            click.echo("Weaviate: ❌ (not ready)")
    except Exception:
        click.echo("Weaviate: ❌")


@cli.group()
def translations():
    """Translation validation commands."""


@translations.command("validate")
@click.option(
    "--frontend-dir",
    default="frontend-react/src/i18n",
    help="Frontend translations directory",
)
@click.option(
    "--backend-dir",
    default="backend/app/translations",
    help="Backend translations directory",
)
@click.option(
    "--languages", default="en,de,fr,es", help="Comma-separated language codes",
)
def validate_translations(frontend_dir, backend_dir, languages):
    """Validate translation files for structure and parameter consistency."""
    langs = [l.strip() for l in languages.split(",") if l.strip()]

    def load_translation_file(file_path: Path):
        try:
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            click.echo(f"Error loading {file_path}: {e}")
            return {}

    def get_all_keys(data, prefix=""):
        keys = set()
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                keys.update(get_all_keys(value, full_key))
            else:
                keys.add(full_key)
        return keys

    def get_nested_value(data, key):
        keys = key.split(".")
        current = data
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return ""
        return str(current) if current is not None else ""

    def validate_translation_files(translation_dir: Path, languages):
        click.echo(f"Validating translation files in {translation_dir}")
        click.echo("=" * 50)
        translations = {}
        for lang in languages:
            file_path = translation_dir / f"{lang}.json"
            if file_path.exists():
                translations[lang] = load_translation_file(file_path)
            else:
                click.echo(f"Warning: Translation file not found: {file_path}")
                translations[lang] = {}
        if not translations:
            click.echo("No translation files found!")
            return False
        all_keys = {}
        for lang, data in translations.items():
            all_keys[lang] = get_all_keys(data)
        reference_lang = "en"
        if reference_lang not in all_keys:
            click.echo(f"Error: Reference language '{reference_lang}' not found!")
            return False
        reference_keys = all_keys[reference_lang]
        click.echo(f"Reference language: {reference_lang} ({len(reference_keys)} keys)")
        all_valid = True
        for lang, keys in all_keys.items():
            if lang == reference_lang:
                continue
            click.echo(f"\nChecking {lang} ({len(keys)} keys):")
            missing_keys = reference_keys - keys
            if missing_keys:
                click.echo(f"  ❌ Missing keys ({len(missing_keys)}):")
                for key in sorted(missing_keys):
                    click.echo(f"    - {key}")
                all_valid = False
            else:
                click.echo("  ✅ No missing keys")
            extra_keys = keys - reference_keys
            if extra_keys:
                click.echo(f"  ⚠️  Extra keys ({len(extra_keys)}):")
                for key in sorted(extra_keys):
                    click.echo(f"    - {key}")
            else:
                click.echo("  ✅ No extra keys")
        return all_valid

    def validate_parameter_consistency(translation_dir: Path, languages):
        click.echo(f"\nValidating parameter consistency in {translation_dir}")
        click.echo("=" * 50)
        translations = {}
        for lang in languages:
            file_path = translation_dir / f"{lang}.json"
            if file_path.exists():
                translations[lang] = load_translation_file(file_path)
        param_keys = {}
        for lang, data in translations.items():
            param_keys[lang] = {}
            keys = get_all_keys(data)
            for key in keys:
                value = get_nested_value(data, key)
                if isinstance(value, str) and "{" in value and "}" in value:
                    import re

                    params = re.findall(r"\{(\w+)\}", value)
                    if params:
                        param_keys[lang][key] = set(params)
        reference_lang = "en"
        if reference_lang not in param_keys:
            return False
        reference_params = param_keys[reference_lang]
        all_consistent = True
        for lang, params in param_keys.items():
            if lang == reference_lang:
                continue
            click.echo(f"\nChecking parameter consistency for {lang}:")
            for key, ref_params in reference_params.items():
                if key in params:
                    lang_params = params[key]
                    if ref_params != lang_params:
                        click.echo(f"  ❌ Parameter mismatch in '{key}':")
                        click.echo(
                            f"    Reference ({reference_lang}): {sorted(ref_params)}",
                        )
                        click.echo(f"    {lang}: {sorted(lang_params)}")
                        all_consistent = False
                    else:
                        click.echo(f"  ✅ Parameters match for '{key}'")
                else:
                    click.echo(f"  ❌ Missing key with parameters: '{key}'")
                    all_consistent = False
        return all_consistent

    frontend_valid = validate_translation_files(Path(frontend_dir), langs)
    backend_valid = validate_translation_files(Path(backend_dir), langs)
    frontend_params_valid = validate_parameter_consistency(Path(frontend_dir), langs)
    backend_params_valid = validate_parameter_consistency(Path(backend_dir), langs)
    click.echo("\n" + "=" * 50)
    click.echo("VALIDATION SUMMARY")
    click.echo("=" * 50)
    click.echo(f"Frontend structure: {'✅ PASS' if frontend_valid else '❌ FAIL'}")
    click.echo(f"Backend structure:  {'✅ PASS' if backend_valid else '❌ FAIL'}")
    click.echo(
        f"Frontend params:    {'✅ PASS' if frontend_params_valid else '❌ FAIL'}",
    )
    click.echo(
        f"Backend params:     {'✅ PASS' if backend_params_valid else '❌ FAIL'}",
    )
    overall_success = (
        frontend_valid
        and backend_valid
        and frontend_params_valid
        and backend_params_valid
    )
    if overall_success:
        click.echo("\n🎉 All validations passed!")
        sys.exit(0)
    else:
        click.echo("\n❌ Some validations failed. Please fix the issues above.")
        sys.exit(1)


@cli.group()
def mcp():
    """MCP integration commands."""


@mcp.command("start-server")
def start_mcp_server():
    """Start the example MCP server for testing."""
    import os as _os
    import sys as _sys

    _sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), "app"))
    from app.tools.example_mcp_server import main as mcp_main

    click.echo("Starting Example MCP Server...")
    click.echo("Server will be available at: http://localhost:8080")
    click.echo("Health check: http://localhost:8080/health")
    click.echo("Press Ctrl+C to stop the server\n")
    try:
        asyncio.run(mcp_main())
    except KeyboardInterrupt:
        click.echo("\nShutting down MCP server...")
    except Exception as e:
        click.echo(f"Error starting MCP server: {e}")
        _sys.exit(1)


@cli.group()
def test():
    """Testing and integration commands."""


@test.command("api-integration")
@click.option("--backend-url", default="http://localhost:8000", help="Backend API URL")
def api_integration(backend_url):
    """Run API integration tests (simuliert scripts/test_api_integration.py)."""
    import asyncio as _asyncio
    import sys as _sys
    from pathlib import Path as _Path

    _sys.path.insert(
        0, str(_Path(__file__).parent.parent / "frontend-react" / "src" / "services"),
    )
    try:
        from api import APIClient
    except ImportError:
        click.echo(
            "❌ Could not import APIClient. Make sure the frontend services are available.",
        )
        _sys.exit(1)

    class APIIntegrationTester:
        def __init__(self, backend_url: str = "http://localhost:8000"):
            self.backend_url = backend_url
            self.api_client = APIClient(backend_url)
            self.test_results = []

        def log_test(self, test_name: str, success: bool, details: str = ""):
            status = "✅ PASS" if success else "❌ FAIL"
            click.echo(f"{status} {test_name}")
            if details:
                click.echo(f"   {details}")
            self.test_results.append(
                {"test": test_name, "success": success, "details": details},
            )

        async def test_health_check(self):
            try:
                response = await self.api_client.health_check()
                if response.success:
                    self.log_test(
                        "Health Check",
                        True,
                        f"Status: {response.data.get('status', 'unknown')}",
                    )
                else:
                    self.log_test("Health Check", False, f"Error: {response.error}")
            except Exception as e:
                self.log_test("Health Check", False, f"Exception: {str(e)}")

        async def test_auth_endpoints(self):
            try:
                test_user = {
                    "email": "test@example.com",
                    "username": "testuser",
                    "password": "TestPassword123!",
                    "full_name": "Test User",
                }
                response = await self.api_client.register(test_user)
                if response.success:
                    self.log_test("User Registration", True)
                else:
                    self.log_test(
                        "User Registration", False, f"Error: {response.error}",
                    )
            except Exception as e:
                self.log_test("User Registration", False, f"Exception: {str(e)}")
            try:
                response = await self.api_client.login(
                    "test@example.com", "TestPassword123!",
                )
                if response.success:
                    self.log_test("User Login", True)
                    if hasattr(response, "data") and response.data:
                        token = response.data.get("access_token")
                        if token:
                            self.api_client.set_token(token)
                else:
                    self.log_test("User Login", False, f"Error: {response.error}")
            except Exception as e:
                self.log_test("User Login", False, f"Exception: {str(e)}")

        async def test_assistant_endpoints(self):
            try:
                response = await self.api_client.get_assistants()
                if response.success:
                    assistants = response.data or []
                    self.log_test(
                        "Get Assistants", True, f"Found {len(assistants)} assistants",
                    )
                else:
                    self.log_test("Get Assistants", False, f"Error: {response.error}")
            except Exception as e:
                self.log_test("Get Assistants", False, f"Exception: {str(e)}")

        async def test_conversation_endpoints(self):
            try:
                response = await self.api_client.get_conversations()
                if response.success:
                    conversations = response.data or []
                    self.log_test(
                        "Get Conversations",
                        True,
                        f"Found {len(conversations)} conversations",
                    )
                else:
                    self.log_test(
                        "Get Conversations", False, f"Error: {response.error}",
                    )
            except Exception as e:
                self.log_test("Get Conversations", False, f"Exception: {str(e)}")

        async def test_tool_endpoints(self):
            try:
                response = await self.api_client.get_tools()
                if response.success:
                    tools = response.data or []
                    self.log_test("Get Tools", True, f"Found {len(tools)} tools")
                else:
                    self.log_test("Get Tools", False, f"Error: {response.error}")
            except Exception as e:
                self.log_test("Get Tools", False, f"Exception: {str(e)}")

        async def test_knowledge_endpoints(self):
            try:
                response = await self.api_client.get_documents()
                if response.success:
                    documents = response.data or []
                    self.log_test(
                        "Get Documents", True, f"Found {len(documents)} documents",
                    )
                else:
                    self.log_test("Get Documents", False, f"Error: {response.error}")
            except Exception as e:
                self.log_test("Get Documents", False, f"Exception: {str(e)}")

        async def test_mcp_endpoints(self):
            try:
                response = await self.api_client.get_mcp_servers()
                if response.success:
                    servers = response.data or []
                    self.log_test(
                        "Get MCP Servers", True, f"Found {len(servers)} servers",
                    )
                else:
                    self.log_test("Get MCP Servers", False, f"Error: {response.error}")
            except Exception as e:
                self.log_test("Get MCP Servers", False, f"Exception: {str(e)}")
            try:
                response = await self.api_client.get_mcp_tools()
                if response.success:
                    tools = response.data or []
                    self.log_test("Get MCP Tools", True, f"Found {len(tools)} tools")
                else:
                    self.log_test("Get MCP Tools", False, f"Error: {response.error}")
            except Exception as e:
                self.log_test("Get MCP Tools", False, f"Exception: {str(e)}")

        async def run_all_tests(self):
            click.echo("🚀 Starting API Integration Tests")
            click.echo("=" * 50)
            await self.test_health_check()
            click.echo("\n🔐 Testing Authentication Endpoints")
            click.echo("-" * 30)
            await self.test_auth_endpoints()
            click.echo("\n🤖 Testing Assistant Endpoints")
            click.echo("-" * 30)
            await self.test_assistant_endpoints()
            click.echo("\n💬 Testing Conversation Endpoints")
            click.echo("-" * 30)
            await self.test_conversation_endpoints()
            click.echo("\n🔧 Testing Tool Endpoints")
            click.echo("-" * 30)
            await self.test_tool_endpoints()
            click.echo("\n📚 Testing Knowledge Base Endpoints")
            click.echo("-" * 30)
            await self.test_knowledge_endpoints()
            click.echo("\n🔌 Testing MCP Endpoints")
            click.echo("-" * 30)
            await self.test_mcp_endpoints()
            click.echo("\n" + "=" * 50)
            click.echo("📊 Integration Test Summary")
            click.echo("=" * 50)
            passed = sum(1 for result in self.test_results if result["success"])
            total = len(self.test_results)
            click.echo(f"Total Tests: {total}")
            click.echo(f"Passed: {passed}")
            click.echo(f"Failed: {total - passed}")
            click.echo(f"Success Rate: {(passed / total) * 100:.1f}%")
            if passed == total:
                click.echo("\n🎉 All integration tests passed!")
            else:
                click.echo("\n⚠️  Some tests failed. Check the details above.")
            return passed == total

    async def main():
        tester = APIIntegrationTester(backend_url)
        success = await tester.run_all_tests()
        _sys.exit(0 if success else 1)

    _asyncio.run(main())


if __name__ == "__main__":
    cli()
