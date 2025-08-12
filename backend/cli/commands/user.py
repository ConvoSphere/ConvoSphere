"""User management commands."""

import sys
from datetime import datetime

from cli.utils.helpers import confirm_action
from cli.utils.output import print_error, print_info, print_success, print_warning
from cli.utils.validation import (
    validate_email,
    validate_password,
    validate_role,
    validate_status,
    validate_username,
)

# App imports


class UserCommands:
    """User management commands."""

    def create_admin(self) -> None:
        """Create admin user interactively."""
        try:
            print_info("Creating admin user...")

            # Get user input
            email = input("Email: ").strip()
            if not validate_email(email):
                print_error("Invalid email format")
                sys.exit(1)

            username = input("Username: ").strip()
            if not validate_username(username):
                print_error(
                    "Invalid username format (3-30 chars, alphanumeric + underscore)"
                )
                sys.exit(1)

            password = input("Password: ").strip()
            if not validate_password(password):
                print_error(
                    "Password must be at least 8 chars with uppercase, lowercase, and digit"
                )
                sys.exit(1)

            first_name = input("First name (optional): ").strip() or None
            last_name = input("Last name (optional): ").strip() or None

            # Create user
            db = next(get_db())

            # Check if user already exists
            existing_user = (
                db.query(User)
                .filter((User.email == email) | (User.username == username))
                .first()
            )

            if existing_user:
                print_error("User with this email or username already exists")
                db.close()
                sys.exit(1)

            # Create new admin user
            hashed_password = get_password_hash(password)
            admin_user = User(
                email=email,
                username=username,
                hashed_password=hashed_password,
                first_name=first_name,
                last_name=last_name,
                role=UserRole.SUPER_ADMIN,
                status=UserStatus.ACTIVE,
                email_verified=True,
                created_at=datetime.utcnow(),
            )

            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            db.close()

            print_success(f"Admin user '{username}' created successfully")

        except (OSError, ValueError, TypeError) as e:
            print_error(f"Failed to create admin user: {str(e)}")
            sys.exit(1)

    def create_secure(self) -> None:
        """Create secure user with strong password."""
        try:
            print_info("Creating secure user...")

            # Generate secure password
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            password = "".join(secrets.choice(alphabet) for _ in range(16))

            # Generate username
            username = f"user_{secrets.token_hex(4)}"
            email = f"{username}@example.com"

            # Create user
            db = next(get_db())

            hashed_password = get_password_hash(password)
            secure_user = User(
                email=email,
                username=username,
                hashed_password=hashed_password,
                role=UserRole.USER,
                status=UserStatus.ACTIVE,
                email_verified=True,
                created_at=datetime.utcnow(),
            )

            db.add(secure_user)
            db.commit()
            db.refresh(secure_user)
            db.close()

            print_success("Secure user created successfully")
            print_info(f"Username: {username}")
            print_info(f"Email: {email}")
            print_info(f"Password: {password}")
            print_warning("Please save these credentials securely!")

        except (OSError, ValueError, TypeError) as e:
            print_error(f"Failed to create secure user: {str(e)}")
            sys.exit(1)

    def list(self) -> None:
        """List all users."""
        try:
            db = next(get_db())
            users = db.query(User).all()

            if not users:
                print_info("No users found")
                db.close()
                return

            print_info(f"Found {len(users)} users:")
            print("-" * 80)
            print(
                f"{'ID':<10} {'Username':<15} {'Email':<25} {'Role':<12} {'Status':<10}"
            )
            print("-" * 80)

            for user in users:
                print(
                    f"{user.id:<10} {user.username:<15} {user.email:<25} {user.role.value:<12} {user.status.value:<10}"
                )

            db.close()

        except (OSError, ValueError, TypeError) as e:
            print_error(f"Failed to list users: {str(e)}")
            sys.exit(1)

    def show(self, identifier: str) -> None:
        """Show user details."""
        try:
            db = next(get_db())

            # Try to find user by ID, email, or username
            user = (
                db.query(User)
                .filter(
                    (User.id == identifier)
                    | (User.email == identifier)
                    | (User.username == identifier)
                )
                .first()
            )

            if not user:
                print_error(f"User not found: {identifier}")
                db.close()
                sys.exit(1)

            print_info(f"User Details for '{user.username}':")
            print(f"  ID: {user.id}")
            print(f"  Email: {user.email}")
            print(f"  Username: {user.username}")
            print(f"  First Name: {user.first_name or 'N/A'}")
            print(f"  Last Name: {user.last_name or 'N/A'}")
            print(f"  Role: {user.role.value}")
            print(f"  Status: {user.status.value}")
            print(f"  Email Verified: {user.email_verified}")
            print(f"  Created At: {user.created_at}")
            print(f"  Last Login: {user.last_login or 'Never'}")

            db.close()

        except (OSError, ValueError, TypeError) as e:
            print_error(f"Failed to show user: {str(e)}")
            sys.exit(1)

    def create(
        self,
        email: str,
        username: str,
        password: str,
        first_name: str = None,
        last_name: str = None,
        role: str = "user",
        status: str = "active",
    ) -> None:
        """Create user with specified parameters."""
        try:
            # Validate inputs
            if not validate_email(email):
                print_error("Invalid email format")
                sys.exit(1)

            if not validate_username(username):
                print_error("Invalid username format")
                sys.exit(1)

            if not validate_password(password):
                print_error("Invalid password format")
                sys.exit(1)

            if not validate_role(role):
                print_error("Invalid role")
                sys.exit(1)

            if not validate_status(status):
                print_error("Invalid status")
                sys.exit(1)

            # Create user
            db = next(get_db())

            # Check if user already exists
            existing_user = (
                db.query(User)
                .filter((User.email == email) | (User.username == username))
                .first()
            )

            if existing_user:
                print_error("User with this email or username already exists")
                db.close()
                sys.exit(1)

            # Create new user
            hashed_password = get_password_hash(password)
            new_user = User(
                email=email,
                username=username,
                hashed_password=hashed_password,
                first_name=first_name,
                last_name=last_name,
                role=UserRole(role),
                status=UserStatus(status),
                email_verified=False,
                created_at=datetime.utcnow(),
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            db.close()

            print_success(f"User '{username}' created successfully")

        except (OSError, ValueError, TypeError) as e:
            print_error(f"Failed to create user: {str(e)}")
            sys.exit(1)

    def update(self, identifier: str, **kwargs) -> None:
        """Update user."""
        try:
            db = next(get_db())

            # Find user
            user = (
                db.query(User)
                .filter(
                    (User.id == identifier)
                    | (User.email == identifier)
                    | (User.username == identifier)
                )
                .first()
            )

            if not user:
                print_error(f"User not found: {identifier}")
                db.close()
                sys.exit(1)

            # Update fields
            if "email" in kwargs:
                if not validate_email(kwargs["email"]):
                    print_error("Invalid email format")
                    db.close()
                    sys.exit(1)
                user.email = kwargs["email"]

            if "username" in kwargs:
                if not validate_username(kwargs["username"]):
                    print_error("Invalid username format")
                    db.close()
                    sys.exit(1)
                user.username = kwargs["username"]

            if "role" in kwargs:
                if not validate_role(kwargs["role"]):
                    print_error("Invalid role")
                    db.close()
                    sys.exit(1)
                user.role = UserRole(kwargs["role"])

            if "status" in kwargs:
                if not validate_status(kwargs["status"]):
                    print_error("Invalid status")
                    db.close()
                    sys.exit(1)
                user.status = UserStatus(kwargs["status"])

            if "first_name" in kwargs:
                user.first_name = kwargs["first_name"]

            if "last_name" in kwargs:
                user.last_name = kwargs["last_name"]

            db.commit()
            db.close()

            print_success(f"User '{user.username}' updated successfully")

        except (OSError, ValueError, TypeError) as e:
            print_error(f"Failed to update user: {str(e)}")
            sys.exit(1)

    def delete(self, identifier: str, confirm: bool = False) -> None:
        """Delete user."""
        try:
            if not confirm:
                if not confirm_action(
                    f"Are you sure you want to delete user '{identifier}'?"
                ):
                    print_info("User deletion cancelled")
                    return

            db = next(get_db())

            # Find user
            user = (
                db.query(User)
                .filter(
                    (User.id == identifier)
                    | (User.email == identifier)
                    | (User.username == identifier)
                )
                .first()
            )

            if not user:
                print_error(f"User not found: {identifier}")
                db.close()
                sys.exit(1)

            username = user.username
            db.delete(user)
            db.commit()
            db.close()

            print_success(f"User '{username}' deleted successfully")

        except (OSError, ValueError, TypeError) as e:
            print_error(f"Failed to delete user: {str(e)}")
            sys.exit(1)

    def reset_password(self) -> None:
        """Reset user password interactively."""
        try:
            print_info("Reset user password...")

            identifier = input("Enter user ID, email, or username: ").strip()

            db = next(get_db())

            # Find user
            user = (
                db.query(User)
                .filter(
                    (User.id == identifier)
                    | (User.email == identifier)
                    | (User.username == identifier)
                )
                .first()
            )

            if not user:
                print_error(f"User not found: {identifier}")
                db.close()
                sys.exit(1)

            # Generate new password
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            new_password = "".join(secrets.choice(alphabet) for _ in range(12))

            # Update password
            user.hashed_password = get_password_hash(new_password)
            db.commit()
            db.close()

            print_success(f"Password reset for user '{user.username}'")
            print_info(f"New password: {new_password}")
            print_warning("Please save this password securely!")

        except (OSError, ValueError, TypeError) as e:
            print_error(f"Failed to reset password: {str(e)}")
            sys.exit(1)
