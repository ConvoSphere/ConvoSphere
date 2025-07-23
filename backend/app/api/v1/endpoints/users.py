"""Users endpoints for user management with enterprise features."""

import psutil
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from opentelemetry.trace import get_current_span
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import check_db_connection, get_db, get_db_info
from app.core.redis_client import check_redis_connection, get_redis_info
from app.core.security import get_current_user
from app.core.weaviate_client import check_weaviate_connection, get_weaviate_info
from app.models.user import AuthProvider, User, UserRole, UserStatus
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
    UserProfileUpdate,
    UserResponse,
    UserSearchParams,
    UserStats,
    UserUpdate,
)
from app.services.user_service import UserService
from app.utils.exceptions import (
    GroupNotFoundError,
    InvalidCredentialsError,
    PermissionDeniedError,
    UserAlreadyExistsError,
    UserLockedError,
    UserNotFoundError,
)

router = APIRouter()


# User CRUD endpoints
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new user."""
    try:
        user_service = UserService(db)
        user = user_service.create_user(user_data, current_user)
        return user_service._user_to_response(user)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/", response_model=UserListResponse)
async def list_users(
    query: str | None = Query(None, description="Search query"),
    role: UserRole | None = Query(None, description="Filter by role"),
    status: UserStatus | None = Query(None, description="Filter by status"),
    auth_provider: AuthProvider | None = Query(
        None, description="Filter by auth provider",
    ),
    organization_id: str | None = Query(None, description="Filter by organization"),
    group_id: str | None = Query(None, description="Filter by group"),
    is_verified: bool | None = Query(None, description="Filter by verification status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List users with filtering and pagination."""
    try:
        search_params = UserSearchParams(
            query=query,
            role=role,
            status=status,
            auth_provider=auth_provider,
            organization_id=organization_id,
            group_id=group_id,
            is_verified=is_verified,
            page=page,
            size=size,
        )

        user_service = UserService(db)
        return user_service.list_users(search_params, current_user)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user by ID."""
    try:
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found",
            )

        # Check if user can access this user
        if (
            not user_service._can_manage_user(current_user, user)
            and user.id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions",
            )

        return user_service._user_to_response(user)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update user."""
    try:
        user_service = UserService(db)
        user = user_service.update_user(user_id, user_data, current_user)
        return user_service._user_to_response(user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete user."""
    try:
        user_service = UserService(db)
        user_service.delete_user(user_id, current_user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# User profile management
@router.get("/me/profile", response_model=UserResponse)
async def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's profile."""
    user_service = UserService(db)
    return user_service._user_to_response(current_user)


@router.put("/me/profile", response_model=UserResponse)
async def update_my_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update current user's profile (including language preference).

    You can update the user's language preference by providing the 'language' field (e.g. 'en', 'de').
    """
    try:
        user_service = UserService(db)
        # Convert profile update to user update
        user_data = UserUpdate(**profile_data.dict(exclude_unset=True))
        user = user_service.update_user(str(current_user.id), user_data, current_user)
        return user_service._user_to_response(user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/me/password", status_code=status.HTTP_200_OK)
async def update_my_password(
    password_data: UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update current user's password."""
    try:
        user_service = UserService(db)
        user_service.update_password(str(current_user.id), password_data)
        return {"message": "Password updated successfully"}
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Bulk operations
@router.post("/bulk-update", status_code=status.HTTP_200_OK)
async def bulk_update_users(
    bulk_data: UserBulkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bulk update users."""
    try:
        user_service = UserService(db)
        updated_count = user_service.bulk_update_users(bulk_data, current_user)
        return {"message": f"Updated {updated_count} users successfully"}
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# User groups management
@router.post(
    "/groups", response_model=UserGroupResponse, status_code=status.HTTP_201_CREATED,
)
async def create_group(
    group_data: UserGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new user group."""
    try:
        user_service = UserService(db)
        group = user_service.create_group(group_data, current_user)
        return user_service._group_to_response(group)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/groups", response_model=list[UserGroupResponse])
async def list_groups(
    organization_id: str | None = Query(None, description="Filter by organization"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user groups."""
    try:
        user_service = UserService(db)
        groups = user_service.list_groups(organization_id, current_user)
        return [user_service._group_to_response(group) for group in groups]
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/groups/{group_id}", response_model=UserGroupResponse)
async def get_group(
    group_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get group by ID."""
    try:
        user_service = UserService(db)
        group = user_service.get_group_by_id(group_id)

        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Group not found",
            )

        return user_service._group_to_response(group)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/groups/{group_id}", response_model=UserGroupResponse)
async def update_group(
    group_id: str,
    group_data: UserGroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update user group."""
    try:
        user_service = UserService(db)
        group = user_service.update_group(group_id, group_data, current_user)
        return user_service._group_to_response(group)
    except GroupNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete user group."""
    try:
        user_service = UserService(db)
        user_service.delete_group(group_id, current_user)
    except GroupNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/groups/assign", status_code=status.HTTP_200_OK)
async def assign_users_to_groups(
    assignment: UserGroupAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Assign users to groups."""
    try:
        user_service = UserService(db)
        updated_count = user_service.assign_users_to_groups(assignment, current_user)
        return {"message": f"Updated {updated_count} users successfully"}
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# SSO user management
@router.post("/sso", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_sso_user(
    sso_data: SSOUserCreate,
    db: Session = Depends(get_db),
):
    """Create user from SSO authentication."""
    try:
        user_service = UserService(db)
        user = user_service.create_sso_user(sso_data)
        return user_service._user_to_response(user)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# User statistics
@router.get("/stats/overview", response_model=UserStats)
async def get_user_stats(
    organization_id: str | None = Query(None, description="Organization ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user statistics."""
    try:
        user_service = UserService(db)
        return user_service.get_user_stats(organization_id, current_user)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# User verification
@router.post("/{user_id}/verify", status_code=status.HTTP_200_OK)
async def verify_user_email(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verify user email."""
    try:
        user_service = UserService(db)
        user_service.verify_email(user_id)
        return {"message": "User email verified successfully"}
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# User search and filtering
@router.get("/search/email/{email}", response_model=UserResponse)
async def get_user_by_email(
    email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user by email."""
    try:
        user_service = UserService(db)
        user = user_service.get_user_by_email(email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found",
            )

        # Check permissions
        if (
            not user_service._can_manage_user(current_user, user)
            and user.id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions",
            )

        return user_service._user_to_response(user)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/search/username/{username}", response_model=UserResponse)
async def get_user_by_username(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user by username."""
    try:
        user_service = UserService(db)
        user = user_service.get_user_by_username(username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found",
            )

        # Check permissions
        if (
            not user_service._can_manage_user(current_user, user)
            and user.id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions",
            )

        return user_service._user_to_response(user)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# User authentication (for internal use)
@router.post("/authenticate", status_code=status.HTTP_200_OK)
async def authenticate_user(
    email: str,
    password: str,
    db: Session = Depends(get_db),
):
    """Authenticate user with email and password."""
    try:
        user_service = UserService(db)
        user = user_service.authenticate_user(email, password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials",
            )

        return {"message": "Authentication successful", "user_id": str(user.id)}
    except UserLockedError as e:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=str(e))
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


def is_admin(user: User) -> bool:
    return user.role in {UserRole.ADMIN, UserRole.SUPER_ADMIN}

@router.get("/admin/default-language", response_model=str)
async def get_default_language(
    current_user: User = Depends(get_current_user),
):
    """Get the global default language (admin only)."""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    settings = get_settings()
    return settings.default_language

@router.put("/admin/default-language", response_model=str)
async def set_default_language(
    language: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
):
    """Set the global default language (admin only)."""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    settings = get_settings()
    # Dynamisch zur Laufzeit setzen (nur für Demo, persistente Speicherung erfordert weitere Logik)
    settings.default_language = language
    return settings.default_language

@router.get("/admin/system-status")
async def get_system_status(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Get system health and performance metrics (admin only)."""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    # System
    cpu = psutil.cpu_percent(interval=0.2)
    ram = psutil.virtual_memory()._asdict()
    # DB
    db_healthy = check_db_connection()
    db_info = get_db_info()
    # Redis
    redis_healthy = await check_redis_connection()
    redis_info = await get_redis_info()
    # Weaviate
    weaviate_healthy = check_weaviate_connection()
    weaviate_info = get_weaviate_info()
    # Fehler (nur Beispiel, kann erweitert werden)
    # Tracing
    span = get_current_span()
    trace_id = span.get_span_context().trace_id if span else None
    return {
        "system": {
            "cpu_percent": cpu,
            "ram": ram,
        },
        "database": {
            "healthy": db_healthy,
            "info": db_info,
        },
        "redis": {
            "healthy": redis_healthy,
            "info": redis_info,
        },
        "weaviate": {
            "healthy": weaviate_healthy,
            "info": weaviate_info,
        },
        "tracing": {
            "trace_id": trace_id,
        },
        "status": "ok" if all([db_healthy, redis_healthy, weaviate_healthy]) else "degraded",
    }
