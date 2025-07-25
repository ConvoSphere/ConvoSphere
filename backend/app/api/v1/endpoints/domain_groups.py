"""
Domain group API endpoints for flexible user organization.

This module provides comprehensive API endpoints for managing domain groups,
including CRUD operations, member management, resource sharing, and invitation handling.
"""

from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.domain_groups import AccessLevel, DomainType, ResourceType
from app.models.user import User
from app.schemas.domain_groups import (
    DomainActivityResponse,
    DomainGroupCreate,
    DomainGroupListResponse,
    DomainGroupResponse,
    DomainGroupStats,
    DomainGroupUpdate,
    DomainHierarchyResponse,
    DomainInvitationCreate,
    DomainInvitationResponse,
    DomainMemberCreate,
    DomainMemberResponse,
    DomainMemberUpdate,
    DomainResourceCreate,
    DomainResourceResponse,
    DomainResourceUpdate,
    DomainSearchParams,
)
from app.services.domain_service import DomainService
from app.utils.exceptions import (
    DomainGroupNotFoundError,
    InvitationNotFoundError,
    PermissionDeniedError,
    ResourceNotFoundError,
    UserNotFoundError,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


# Domain Group CRUD Operations
@router.post(
    "/",
    response_model=DomainGroupResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_domain_group(
    domain_data: DomainGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new domain group."""
    try:
        domain_service = DomainService(db)
        domain_group = domain_service.create_domain_group(domain_data, current_user)
        return _domain_group_to_response(domain_group)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except DomainGroupNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", response_model=DomainGroupListResponse)
async def list_domain_groups(
    query: str | None = Query(None, description="Search query"),
    domain_type: DomainType | None = Query(None, description="Filter by domain type"),
    organization_id: str | None = Query(None, description="Filter by organization"),
    parent_domain_id: str | None = Query(None, description="Filter by parent domain"),
    is_public: bool | None = Query(None, description="Filter by public status"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    tags: list[str] | None = Query(None, description="Filter by tags"),
    created_after: datetime | None = Query(
        None,
        description="Filter by creation date (after)",
    ),
    created_before: datetime | None = Query(
        None,
        description="Filter by creation date (before)",
    ),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List domain groups with filtering and pagination."""
    try:
        search_params = DomainSearchParams(
            query=query,
            domain_type=domain_type,
            organization_id=organization_id,
            parent_domain_id=parent_domain_id,
            is_public=is_public,
            is_active=is_active,
            tags=tags,
            created_after=created_after,
            created_before=created_before,
            page=page,
            size=size,
        )

        domain_service = DomainService(db)
        result = domain_service.list_domain_groups(search_params, current_user)

        return DomainGroupListResponse(
            domains=[_domain_group_to_response(d) for d in result["domains"]],
            total=result["total"],
            page=result["page"],
            size=result["size"],
            pages=result["pages"],
        )
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/{domain_id}", response_model=DomainGroupResponse)
async def get_domain_group(
    domain_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get domain group by ID."""
    try:
        domain_service = DomainService(db)
        domain_group = domain_service.get_domain_group_by_id(domain_id, current_user)
        if not domain_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain group not found",
            )
        return _domain_group_to_response(domain_group)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/{domain_id}", response_model=DomainGroupResponse)
async def update_domain_group(
    domain_id: str,
    domain_data: DomainGroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update domain group."""
    try:
        domain_service = DomainService(db)
        domain_group = domain_service.update_domain_group(
            domain_id,
            domain_data,
            current_user,
        )
        return _domain_group_to_response(domain_group)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except DomainGroupNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_domain_group(
    domain_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete domain group."""
    try:
        domain_service = DomainService(db)
        domain_service.delete_domain_group(domain_id, current_user)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except DomainGroupNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Member Management
@router.post(
    "/{domain_id}/members",
    response_model=DomainMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_domain_member(
    domain_id: str,
    member_data: DomainMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add member to domain group."""
    try:
        domain_service = DomainService(db)
        success = domain_service.add_domain_member(domain_id, member_data, current_user)
        if success:
            # Return member information
            return _get_member_response(domain_id, member_data.user_id, db)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add member",
        )
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except DomainGroupNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{domain_id}/members", response_model=list[DomainMemberResponse])
async def list_domain_members(
    domain_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List domain group members."""
    try:
        domain_service = DomainService(db)
        domain_group = domain_service.get_domain_group_by_id(domain_id, current_user)
        if not domain_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain group not found",
            )

        # Get members with user information
        members = []
        for member in domain_group.members:
            members.append(_get_member_response(domain_id, str(member.id), db))

        return members
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/{domain_id}/members/{user_id}", response_model=DomainMemberResponse)
async def update_domain_member(
    domain_id: str,
    user_id: str,
    member_data: DomainMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update domain member."""
    try:
        domain_service = DomainService(db)
        success = domain_service.update_domain_member(
            domain_id,
            user_id,
            member_data,
            current_user,
        )
        if success:
            return _get_member_response(domain_id, user_id, db)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update member",
        )
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except DomainGroupNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{domain_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_domain_member(
    domain_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove member from domain group."""
    try:
        domain_service = DomainService(db)
        domain_service.remove_domain_member(domain_id, user_id, current_user)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except DomainGroupNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Resource Management
@router.post(
    "/{domain_id}/resources",
    response_model=DomainResourceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_domain_resource(
    domain_id: str,
    resource_data: DomainResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add resource to domain group."""
    try:
        domain_service = DomainService(db)
        resource = domain_service.add_domain_resource(
            domain_id,
            resource_data,
            current_user,
        )
        return _domain_resource_to_response(resource)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except DomainGroupNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{domain_id}/resources", response_model=list[DomainResourceResponse])
async def list_domain_resources(
    domain_id: str,
    resource_type: ResourceType | None = Query(
        None,
        description="Filter by resource type",
    ),
    is_active: bool | None = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List domain group resources."""
    try:
        domain_service = DomainService(db)
        domain_group = domain_service.get_domain_group_by_id(domain_id, current_user)
        if not domain_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain group not found",
            )

        # Get resources with filtering
        resources = domain_group.resources
        if resource_type:
            resources = resources.filter_by(resource_type=resource_type)
        if is_active is not None:
            resources = resources.filter_by(is_active=is_active)

        return [_domain_resource_to_response(r) for r in resources.all()]
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/{domain_id}/resources/{resource_id}",
    response_model=DomainResourceResponse,
)
async def get_domain_resource(
    domain_id: str,
    resource_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get domain resource by ID."""
    try:
        domain_service = DomainService(db)
        domain_group = domain_service.get_domain_group_by_id(domain_id, current_user)
        if not domain_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain group not found",
            )

        resource = domain_group.resources.filter_by(
            resource_id=resource_id,
            is_active=True,
        ).first()
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found",
            )

        return _domain_resource_to_response(resource)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put(
    "/{domain_id}/resources/{resource_id}",
    response_model=DomainResourceResponse,
)
async def update_domain_resource(
    domain_id: str,
    resource_id: str,
    resource_data: DomainResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update domain resource."""
    try:
        domain_service = DomainService(db)
        resource = domain_service.update_domain_resource(
            domain_id,
            resource_id,
            resource_data,
            current_user,
        )
        return _domain_resource_to_response(resource)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except DomainGroupNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{domain_id}/resources/{resource_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_domain_resource(
    domain_id: str,
    resource_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove resource from domain group."""
    try:
        domain_service = DomainService(db)
        domain_service.remove_domain_resource(domain_id, resource_id, current_user)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except DomainGroupNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Invitation Management
@router.post(
    "/{domain_id}/invitations",
    response_model=DomainInvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_domain_invitation(
    domain_id: str,
    invitation_data: DomainInvitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create domain invitation."""
    try:
        domain_service = DomainService(db)
        invitation = domain_service.create_domain_invitation(
            domain_id,
            invitation_data,
            current_user,
        )
        return _domain_invitation_to_response(invitation)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except DomainGroupNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{domain_id}/invitations", response_model=list[DomainInvitationResponse])
async def list_domain_invitations(
    domain_id: str,
    status: str | None = Query(None, description="Filter by invitation status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List domain invitations."""
    try:
        domain_service = DomainService(db)
        domain_group = domain_service.get_domain_group_by_id(domain_id, current_user)
        if not domain_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain group not found",
            )

        # Get invitations with filtering
        from app.models.domain_groups import DomainInvitation

        query = db.query(DomainInvitation).filter(
            DomainInvitation.domain_group_id == domain_id,
        )
        if status:
            query = query.filter(DomainInvitation.status == status)

        invitations = query.all()
        return [_domain_invitation_to_response(i) for i in invitations]
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/invitations/{token}/accept", status_code=status.HTTP_200_OK)
async def accept_domain_invitation(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Accept domain invitation."""
    try:
        domain_service = DomainService(db)
        success = domain_service.accept_domain_invitation(token, current_user)
        if success:
            return {"message": "Invitation accepted successfully"}
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to accept invitation",
        )
    except InvitationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# Activity and Analytics
@router.get("/{domain_id}/activities", response_model=list[DomainActivityResponse])
async def list_domain_activities(
    domain_id: str,
    activity_type: str | None = Query(None, description="Filter by activity type"),
    resource_type: ResourceType | None = Query(
        None,
        description="Filter by resource type",
    ),
    limit: int = Query(50, ge=1, le=200, description="Number of activities to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List domain activities."""
    try:
        domain_service = DomainService(db)
        domain_group = domain_service.get_domain_group_by_id(domain_id, current_user)
        if not domain_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain group not found",
            )

        # Get activities with filtering
        from app.models.domain_groups import DomainActivity

        query = db.query(DomainActivity).filter(
            DomainActivity.domain_group_id == domain_id,
        )

        if activity_type:
            query = query.filter(DomainActivity.activity_type == activity_type)
        if resource_type:
            query = query.filter(DomainActivity.resource_type == resource_type)

        activities = query.order_by(DomainActivity.created_at.desc()).limit(limit).all()
        return [_domain_activity_to_response(a) for a in activities]
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/stats", response_model=DomainGroupStats)
async def get_domain_stats(
    organization_id: str | None = Query(None, description="Organization ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get domain group statistics."""
    try:
        domain_service = DomainService(db)
        return domain_service.get_domain_stats(organization_id, current_user)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# Hierarchy Management
@router.get("/hierarchy", response_model=list[DomainHierarchyResponse])
async def get_domain_hierarchy(
    organization_id: str | None = Query(None, description="Organization ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get domain group hierarchy."""
    try:
        DomainService(db)
        # This would implement hierarchy building logic
        # For now, return a placeholder
        return []
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# Helper Functions
def _domain_group_to_response(domain_group) -> DomainGroupResponse:
    """Convert domain group to response model."""
    return DomainGroupResponse(
        id=domain_group.id,
        name=domain_group.name,
        description=domain_group.description,
        display_name=domain_group.display_name,
        domain_type=domain_group.domain_type,
        parent_domain_id=domain_group.parent_domain_id,
        organization_id=domain_group.organization_id,
        external_id=domain_group.external_id,
        tags=domain_group.tags,
        is_public=domain_group.is_public,
        default_access_level=domain_group.default_access_level,
        allow_self_join=domain_group.allow_self_join,
        require_approval=domain_group.require_approval,
        settings=domain_group.settings,
        permissions=domain_group.permissions,
        is_active=domain_group.is_active,
        is_system=domain_group.is_system,
        member_count=domain_group.member_count,
        resource_count=domain_group.resource_count,
        created_at=domain_group.created_at,
        updated_at=domain_group.updated_at,
        expires_at=domain_group.expires_at,
        is_expired=domain_group.is_expired,
    )


def _domain_resource_to_response(resource) -> DomainResourceResponse:
    """Convert domain resource to response model."""
    return DomainResourceResponse(
        id=resource.id,
        domain_group_id=resource.domain_group_id,
        resource_id=resource.resource_id,
        resource_type=resource.resource_type,
        resource_name=resource.resource_name,
        access_level=resource.access_level,
        is_public=resource.is_public,
        description=resource.description,
        tags=resource.tags,
        metadata=resource.metadata,
        is_active=resource.is_active,
        added_at=resource.added_at,
        updated_at=resource.updated_at,
        expires_at=resource.expires_at,
        added_by=resource.added_by,
        is_expired=resource.is_expired,
    )


def _domain_invitation_to_response(invitation) -> DomainInvitationResponse:
    """Convert domain invitation to response model."""
    return DomainInvitationResponse(
        id=invitation.id,
        domain_group_id=invitation.domain_group_id,
        email=invitation.email,
        user_id=invitation.user_id,
        access_level=invitation.access_level,
        message=invitation.message,
        status=invitation.status,
        token=invitation.token,
        expires_at=invitation.expires_at,
        created_at=invitation.created_at,
        accepted_at=invitation.accepted_at,
        is_expired=invitation.is_expired,
    )


def _domain_activity_to_response(activity) -> DomainActivityResponse:
    """Convert domain activity to response model."""
    return DomainActivityResponse(
        id=activity.id,
        domain_group_id=activity.domain_group_id,
        user_id=activity.user_id,
        activity_type=activity.activity_type,
        resource_type=activity.resource_type,
        resource_id=activity.resource_id,
        description=activity.description,
        details=activity.details,
        created_at=activity.created_at,
        user_email=activity.user.email if activity.user else None,
        user_name=activity.user.full_name if activity.user else None,
    )


def _get_member_response(
    domain_id: str,
    user_id: str,
    db: Session,
) -> DomainMemberResponse:
    """Get member response with user information."""
    from app.models.domain_groups import DomainGroup
    from app.models.user import User

    user = db.query(User).filter(User.id == user_id).first()
    domain_group = db.query(DomainGroup).filter(DomainGroup.id == domain_id).first()

    if not user or not domain_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User or domain not found",
        )

    # Get member access level
    member = domain_group.members.filter_by(id=user_id).first()
    access_level = member.access_level if member else AccessLevel.READ_ONLY

    return DomainMemberResponse(
        user_id=user.id,
        access_level=access_level,
        is_active=member.is_active if member else False,
        joined_at=member.joined_at if member else datetime.now(),
        invited_by=member.invited_by if member else None,
        user_email=user.email,
        user_name=user.full_name,
        user_role=user.role,
    )
