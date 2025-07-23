"""User service for managing users with enterprise features."""

from datetime import UTC, datetime, timedelta

from passlib.context import CryptContext
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_password_hash, verify_password
from app.models.user import AuthProvider, User, UserGroup, UserRole, UserStatus
from app.schemas.user import (
    SSOUserCreate,
    UserBulkUpdate,
    UserCreate,
    UserGroupAssignment,
    UserGroupCreate,
    UserGroupResponse,
    UserGroupUpdate,
    UserListResponse,
    UserPasswordUpdate,
    UserResponse,
    UserSearchParams,
    UserStats,
    UserUpdate,
)
from app.utils.exceptions import (
    GroupNotFoundError,
    InvalidCredentialsError,
    PermissionDeniedError,
    UserAlreadyExistsError,
    UserLockedError,
    UserNotFoundError,
)


class UserService:
    """Service for managing users with enterprise features."""

    def __init__(self, db: Session):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # User CRUD operations
    def create_user(
        self, user_data: UserCreate, current_user: User | None = None,
    ) -> User:
        """Create a new user."""
        # Check if user already exists
        if self.get_user_by_email(user_data.email):
            raise UserAlreadyExistsError(
                f"User with email {user_data.email} already exists",
            )

        if self.get_user_by_username(user_data.username):
            raise UserAlreadyExistsError(
                f"User with username {user_data.username} already exists",
            )

        # Hash password if provided
        hashed_password = None
        if user_data.password:
            hashed_password = get_password_hash(user_data.password)

        # Create user
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            display_name=user_data.display_name,
            avatar_url=user_data.avatar_url,
            bio=user_data.bio,
            phone=user_data.phone,
            organization_id=user_data.organization_id,
            department=user_data.department,
            job_title=user_data.job_title,
            employee_id=user_data.employee_id,
            auth_provider=user_data.auth_provider,
            external_id=user_data.external_id,
            sso_attributes=user_data.sso_attributes,
            status=user_data.status,
            role=user_data.role,
            language=user_data.language,
            timezone=user_data.timezone,
            preferences=user_data.preferences,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Assign groups if provided
        if user_data.group_ids:
            self.assign_user_to_groups(user.id, user_data.group_ids)

        return user

    def get_user_by_id(self, user_id: str) -> User | None:
        """Get user by ID."""
        return (
            self.db.query(User)
            .options(
                joinedload(User.groups),
            )
            .filter(User.id == user_id)
            .first()
        )

    def get_user_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return (
            self.db.query(User)
            .options(
                joinedload(User.groups),
            )
            .filter(User.email == email)
            .first()
        )

    def get_user_by_username(self, username: str) -> User | None:
        """Get user by username."""
        return (
            self.db.query(User)
            .options(
                joinedload(User.groups),
            )
            .filter(User.username == username)
            .first()
        )

    def get_user_by_external_id(
        self, external_id: str, auth_provider: AuthProvider,
    ) -> User | None:
        """Get user by external ID and auth provider."""
        return (
            self.db.query(User)
            .options(
                joinedload(User.groups),
            )
            .filter(
                and_(
                    User.external_id == external_id, User.auth_provider == auth_provider,
                ),
            )
            .first()
        )

    def update_user(
        self, user_id: str, user_data: UserUpdate, current_user: User,
    ) -> User:
        """Update user."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Check permissions
        if not self._can_manage_user(current_user, user):
            raise PermissionDeniedError

        # Update fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(user)

        return user

    def delete_user(self, user_id: str, current_user: User) -> bool:
        """Delete user."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Check permissions
        if not self._can_manage_user(current_user, user):
            raise PermissionDeniedError

        # Don't allow deletion of super admins
        if user.role == UserRole.SUPER_ADMIN:
            raise PermissionDeniedError

        self.db.delete(user)
        self.db.commit()
        return True

    def list_users(
        self, search_params: UserSearchParams, current_user: User,
    ) -> UserListResponse:
        """List users with filtering and pagination."""
        query = self.db.query(User).options(joinedload(User.groups))

        # Apply filters
        if search_params.query:
            search_term = f"%{search_params.query}%"
            query = query.filter(
                or_(
                    User.email.ilike(search_term),
                    User.username.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    User.display_name.ilike(search_term),
                ),
            )

        if search_params.role:
            query = query.filter(User.role == search_params.role)

        if search_params.status:
            query = query.filter(User.status == search_params.status)

        if search_params.auth_provider:
            query = query.filter(User.auth_provider == search_params.auth_provider)

        if search_params.organization_id:
            query = query.filter(User.organization_id == search_params.organization_id)

        if search_params.group_id:
            query = query.join(User.groups).filter(
                UserGroup.id == search_params.group_id,
            )

        if search_params.is_verified is not None:
            query = query.filter(User.is_verified == search_params.is_verified)

        if search_params.created_after:
            query = query.filter(User.created_at >= search_params.created_after)

        if search_params.created_before:
            query = query.filter(User.created_at <= search_params.created_before)

        if search_params.last_login_after:
            query = query.filter(User.last_login >= search_params.last_login_after)

        if search_params.last_login_before:
            query = query.filter(User.last_login <= search_params.last_login_before)

        # Apply organization scope for non-super admins
        if current_user.role != UserRole.SUPER_ADMIN:
            query = query.filter(User.organization_id == current_user.organization_id)

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (search_params.page - 1) * search_params.size
        users = query.offset(offset).limit(search_params.size).all()

        # Convert to response models
        user_responses = []
        for user in users:
            user_response = self._user_to_response(user)
            user_responses.append(user_response)

        pages = (total + search_params.size - 1) // search_params.size

        return UserListResponse(
            users=user_responses,
            total=total,
            page=search_params.page,
            size=search_params.size,
            pages=pages,
        )

    def bulk_update_users(self, bulk_data: UserBulkUpdate, current_user: User) -> int:
        """Bulk update users."""
        # Check permissions
        if not current_user.has_permission("user:write"):
            raise PermissionDeniedError

        # Get users to update
        users = self.db.query(User).filter(User.id.in_(bulk_data.user_ids)).all()

        # Apply updates
        update_data = bulk_data.dict(exclude_unset=True, exclude={"user_ids"})
        updated_count = 0

        for user in users:
            # Check if current user can manage this user
            if not self._can_manage_user(current_user, user):
                continue

            for field, value in update_data.items():
                if field != "group_ids":
                    setattr(user, field, value)

            user.updated_at = datetime.now(UTC)
            updated_count += 1

        # Handle group assignments
        if bulk_data.group_ids is not None:
            for user in users:
                if self._can_manage_user(current_user, user):
                    self.assign_user_to_groups(user.id, bulk_data.group_ids)

        self.db.commit()
        return updated_count

    # User authentication and security
    def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate user with email and password."""
        user = self.get_user_by_email(email)
        if not user:
            return None

        # Check if user is locked
        if user.is_locked:
            raise UserLockedError

        # Check if user is active
        if not user.is_active:
            return None

        # Verify password
        if not verify_password(password, user.hashed_password):
            # Increment failed login attempts
            failed_attempts = int(user.failed_login_attempts) + 1
            user.failed_login_attempts = str(failed_attempts)

            # Lock account after 5 failed attempts
            if failed_attempts >= 5:
                user.locked_until = datetime.now(UTC) + timedelta(minutes=30)

            self.db.commit()
            return None

        # Reset failed login attempts on successful login
        user.failed_login_attempts = "0"
        user.locked_until = None
        user.last_login = datetime.now(UTC)
        user.last_activity = datetime.now(UTC)
        self.db.commit()

        return user

    def update_password(self, user_id: str, password_data: UserPasswordUpdate) -> bool:
        """Update user password."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Verify current password
        if not verify_password(password_data.current_password, user.hashed_password):
            raise InvalidCredentialsError

        # Update password
        user.hashed_password = get_password_hash(password_data.new_password)
        user.password_changed_at = datetime.now(UTC)
        user.updated_at = datetime.now(UTC)

        self.db.commit()
        return True

    def verify_email(self, user_id: str) -> bool:
        """Verify user email."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        user.is_verified = True
        user.email_verified_at = datetime.now(UTC)
        user.updated_at = datetime.now(UTC)

        self.db.commit()
        return True

    # SSO user management
    def create_sso_user(self, sso_data: SSOUserCreate) -> User:
        """Create user from SSO authentication."""
        # Check if user already exists
        existing_user = self.get_user_by_external_id(
            sso_data.external_id, sso_data.auth_provider,
        )
        if existing_user:
            return existing_user

        # Generate username if not provided
        username = sso_data.username
        if not username:
            base_username = sso_data.email.split("@")[0]
            username = base_username
            counter = 1
            while self.get_user_by_username(username):
                username = f"{base_username}{counter}"
                counter += 1

        # Create user
        user_data = UserCreate(
            email=sso_data.email,
            username=username,
            first_name=sso_data.first_name,
            last_name=sso_data.last_name,
            display_name=sso_data.display_name,
            avatar_url=sso_data.avatar_url,
            auth_provider=sso_data.auth_provider,
            external_id=sso_data.external_id,
            sso_attributes=sso_data.sso_attributes,
            organization_id=sso_data.organization_id,
            role=sso_data.role,
            group_ids=sso_data.group_ids,
            status=UserStatus.ACTIVE,
            is_verified=True,
        )

        return self.create_user(user_data)

    # User groups management
    def create_group(
        self, group_data: UserGroupCreate, current_user: User,
    ) -> UserGroup:
        """Create a new user group."""
        if not current_user.has_permission("group:write"):
            raise PermissionDeniedError("Insufficient permissions to create groups")

        group = UserGroup(
            name=group_data.name,
            description=group_data.description,
            organization_id=group_data.organization_id or current_user.organization_id,
            permissions=group_data.permissions,
            settings=group_data.settings,
        )

        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)

        return group

    def get_group_by_id(self, group_id: str) -> UserGroup | None:
        """Get group by ID."""
        return (
            self.db.query(UserGroup)
            .options(
                joinedload(UserGroup.users),
            )
            .filter(UserGroup.id == group_id)
            .first()
        )

    def update_group(
        self, group_id: str, group_data: UserGroupUpdate, current_user: User,
    ) -> UserGroup:
        """Update user group."""
        group = self.get_group_by_id(group_id)
        if not group:
            raise GroupNotFoundError(group_id)

        if not current_user.has_permission("group:write"):
            raise PermissionDeniedError

        # Don't allow updating system groups
        if group.is_system:
            raise PermissionDeniedError

        update_data = group_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(group, field, value)

        group.updated_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(group)

        return group

    def delete_group(self, group_id: str, current_user: User) -> bool:
        """Delete user group."""
        group = self.get_group_by_id(group_id)
        if not group:
            raise GroupNotFoundError(group_id)

        if not current_user.has_permission("group:delete"):
            raise PermissionDeniedError

        # Don't allow deletion of system groups
        if group.is_system:
            raise PermissionDeniedError

        self.db.delete(group)
        self.db.commit()
        return True

    def list_groups(
        self, organization_id: str | None = None, current_user: User = None,
    ) -> list[UserGroup]:
        """List user groups."""
        query = self.db.query(UserGroup).options(joinedload(UserGroup.users))

        if organization_id:
            query = query.filter(UserGroup.organization_id == organization_id)
        elif current_user and current_user.role != UserRole.SUPER_ADMIN:
            query = query.filter(
                UserGroup.organization_id == current_user.organization_id,
            )

        return query.all()

    def assign_user_to_groups(self, user_id: str, group_ids: list[str]) -> bool:
        """Assign user to groups."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")

        groups = self.db.query(UserGroup).filter(UserGroup.id.in_(group_ids)).all()

        # Clear existing group assignments and add new ones
        user.groups = groups
        self.db.commit()

        return True

    def assign_users_to_groups(
        self, assignment: UserGroupAssignment, current_user: User,
    ) -> int:
        """Assign multiple users to groups."""
        if not current_user.has_permission("user:write"):
            raise PermissionDeniedError(
                "Insufficient permissions for group assignments",
            )

        users = self.db.query(User).filter(User.id.in_(assignment.user_ids)).all()
        groups = (
            self.db.query(UserGroup)
            .filter(UserGroup.id.in_(assignment.group_ids))
            .all()
        )

        updated_count = 0
        for user in users:
            if self._can_manage_user(current_user, user):
                if assignment.operation == "add":
                    user.groups.extend([g for g in groups if g not in user.groups])
                elif assignment.operation == "remove":
                    user.groups = [g for g in user.groups if g not in groups]
                updated_count += 1

        self.db.commit()
        return updated_count

    # User statistics
    def get_user_stats(
        self, organization_id: str | None = None, current_user: User = None,
    ) -> UserStats:
        """Get user statistics."""
        query = self.db.query(User)

        if organization_id:
            query = query.filter(User.organization_id == organization_id)
        elif current_user and current_user.role != UserRole.SUPER_ADMIN:
            query = query.filter(User.organization_id == current_user.organization_id)

        total_users = query.count()

        # Status counts
        active_users = query.filter(User.status == UserStatus.ACTIVE).count()
        inactive_users = query.filter(User.status == UserStatus.INACTIVE).count()
        suspended_users = query.filter(User.status == UserStatus.SUSPENDED).count()
        pending_users = query.filter(User.status == UserStatus.PENDING).count()
        verified_users = query.filter(User.is_verified.is_(True)).count()

        # Role counts
        users_by_role = {}
        for role in UserRole:
            count = query.filter(User.role == role).count()
            users_by_role[role.value] = count

        # Auth provider counts
        users_by_auth_provider = {}
        for provider in AuthProvider:
            count = query.filter(User.auth_provider == provider).count()
            users_by_auth_provider[provider.value] = count

        # Status counts
        users_by_status = {}
        for status in UserStatus:
            count = query.filter(User.status == status).count()
            users_by_status[status.value] = count

        # Recent activity
        thirty_days_ago = datetime.now(UTC) - timedelta(days=30)
        seven_days_ago = datetime.now(UTC) - timedelta(days=7)

        recent_registrations = query.filter(User.created_at >= thirty_days_ago).count()
        recent_logins = query.filter(User.last_login >= seven_days_ago).count()

        return UserStats(
            total_users=total_users,
            active_users=active_users,
            inactive_users=inactive_users,
            suspended_users=suspended_users,
            pending_users=pending_users,
            verified_users=verified_users,
            users_by_role=users_by_role,
            users_by_auth_provider=users_by_auth_provider,
            users_by_status=users_by_status,
            recent_registrations=recent_registrations,
            recent_logins=recent_logins,
        )

    # Helper methods
    def _can_manage_user(self, current_user: User, target_user: User) -> bool:
        """Check if current user can manage target user."""
        if current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            return True

        if current_user.role == UserRole.MANAGER:
            # Managers can manage users in their groups
            return any(group in current_user.groups for group in target_user.groups)

        return False

    def _user_to_response(self, user: User) -> UserResponse:
        """Convert User model to UserResponse."""
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
            phone=user.phone,
            organization_id=user.organization_id,
            department=user.department,
            job_title=user.job_title,
            employee_id=user.employee_id,
            auth_provider=user.auth_provider,
            external_id=user.external_id,
            status=user.status,
            role=user.role,
            language=user.language,
            timezone=user.timezone,
            preferences=user.preferences,
            is_verified=user.is_verified,
            email_verified_at=user.email_verified_at,
            password_changed_at=user.password_changed_at,
            failed_login_attempts=user.failed_login_attempts,
            locked_until=user.locked_until,
            last_login=user.last_login,
            last_activity=user.last_activity,
            created_at=user.created_at,
            updated_at=user.updated_at,
            groups=[self._group_to_response(group) for group in user.groups],
            effective_permissions=user.get_effective_permissions(),
            full_name=user.full_name,
            is_active=user.is_active,
            is_locked=user.is_locked,
        )

    def _group_to_response(self, group: UserGroup) -> UserGroupResponse:
        """Convert UserGroup model to UserGroupResponse."""
        return UserGroupResponse(
            id=group.id,
            name=group.name,
            description=group.description,
            organization_id=group.organization_id,
            permissions=group.permissions,
            settings=group.settings,
            is_active=group.is_active,
            is_system=group.is_system,
            created_at=group.created_at,
            updated_at=group.updated_at,
            user_count=len(group.users) if group.users else 0,
        )
