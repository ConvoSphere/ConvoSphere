"""Development tools commands."""

import random
import subprocess
import sys
from datetime import datetime

import requests

from cli.utils.output import print_error, print_info, print_success, print_warning

# Constants
HTTP_OK = 200
TIMEOUT_SECONDS = 5


class DevCommands:
    """Development tools commands."""

    def quality_check(self) -> None:
        """Run code quality checks."""
        try:
            print_info("Running code quality checks...")

            # Run ruff
            try:
                result = subprocess.run(
                    ["ruff", "check", "backend/"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    print_success("Ruff check passed")
                else:
                    print_error("Ruff check failed:")
                    print(result.stdout)
                    print(result.stderr)
            except FileNotFoundError:
                print_error("Ruff not found. Install with: pip install ruff")

            # Run mypy
            try:
                result = subprocess.run(
                    ["mypy", "backend/"], capture_output=True, text=True, check=False
                )
                if result.returncode == 0:
                    print_success("MyPy check passed")
                else:
                    print_error("MyPy check failed:")
                    print(result.stdout)
                    print(result.stderr)
            except FileNotFoundError:
                print_error("MyPy not found. Install with: pip install mypy")

            # Run tests
            try:
                result = subprocess.run(
                    ["pytest", "tests/", "-v"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    print_success("Tests passed")
                else:
                    print_error("Tests failed:")
                    print(result.stdout)
                    print(result.stderr)
            except FileNotFoundError:
                print_error("Pytest not found. Install with: pip install pytest")

        except (OSError, subprocess.SubprocessError) as e:
            print_error(f"Quality check failed: {str(e)}")
            sys.exit(1)

    def api_test(self, url: str = "http://localhost:8000") -> None:
        """Test API endpoints."""
        try:
            print_info(f"Testing API at: {url}")

            # Test health endpoint
            try:
                response = requests.get(f"{url}/health", timeout=TIMEOUT_SECONDS)
                if response.status_code == HTTP_OK:
                    print_success("Health endpoint: OK")
                else:
                    print_error(f"Health endpoint: ERROR - {response.status_code}")
            except requests.exceptions.RequestException as e:
                print_error(f"Health endpoint: ERROR - {str(e)}")

            # Test docs endpoint
            try:
                response = requests.get(f"{url}/docs", timeout=TIMEOUT_SECONDS)
                if response.status_code == HTTP_OK:
                    print_success("Docs endpoint: OK")
                else:
                    print_error(f"Docs endpoint: ERROR - {response.status_code}")
            except requests.exceptions.RequestException as e:
                print_error(f"Docs endpoint: ERROR - {str(e)}")

            # Test API version endpoint
            try:
                response = requests.get(f"{url}/api/v1/", timeout=TIMEOUT_SECONDS)
                if response.status_code == HTTP_OK:
                    print_success("API v1 endpoint: OK")
                else:
                    print_error(f"API v1 endpoint: ERROR - {response.status_code}")
            except requests.exceptions.RequestException as e:
                print_error(f"API v1 endpoint: ERROR - {str(e)}")

        except (requests.RequestException, OSError) as e:
            print_error(f"API test failed: {str(e)}")
            sys.exit(1)

    def test_data(self, users: int = 5) -> None:
        """Generate test data."""
        try:
            print_info(f"Generating {users} test users...")

            db = next(get_db())

            # Generate test users
            for i in range(users):
                username = f"testuser{i + 1}"
                email = f"test{i + 1}@example.com"
                password = "".join(
                    random.choices(string.ascii_letters + string.digits, k=12)
                )

                # Check if user already exists
                existing_user = (
                    db.query(User)
                    .filter((User.email == email) | (User.username == username))
                    .first()
                )

                if existing_user:
                    print_info(f"User {username} already exists, skipping...")
                    continue

                # Create test user
                hashed_password = get_password_hash(password)
                test_user = User(
                    email=email,
                    username=username,
                    hashed_password=hashed_password,
                    first_name=f"Test{i + 1}",
                    last_name="User",
                    role=UserRole.USER,
                    status=UserStatus.ACTIVE,
                    email_verified=True,
                    created_at=datetime.utcnow(),
                )

                db.add(test_user)
                print_info(f"Created test user: {username} (password: {password})")

            db.commit()
            db.close()

            print_success(f"Generated {users} test users successfully")
            print_warning("Please save the passwords securely!")

        except (OSError, ValueError, TypeError) as e:
            print_error(f"Failed to generate test data: {str(e)}")
            sys.exit(1)
