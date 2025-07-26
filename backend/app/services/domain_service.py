"""
Domain group service for managing flexible user organization.

This service provides comprehensive domain group management including
CRUD operations, member management, resource sharing, and invitation handling.
"""

import secrets
from datetime import datetime, timedelta
from typing import Any

from backend.app.models.domain_groups import (
    AccessLevel,
    DomainActivity,
    DomainGroup,
    DomainInvitation,
    DomainResource,
    DomainType,
    ResourceType,
)
from backend.app.models.user import User, UserRole
from backend.app.schemas.domain_groups import (
    DomainGroupCreate,
    DomainGroupStats,
    DomainGroupUpdate,
    DomainInvitationCreate,
    DomainMemberCreate,
    DomainMemberUpdate,
    DomainResourceCreate,
    DomainResourceUpdate,
    DomainSearchParams,
)
from backend.app.utils.exceptions import (
    DomainGroupNotFoundError,
    InvitationNotFoundError,
    PermissionDeniedError,
    ResourceNotFoundError,
    UserNotFoundError,
)
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload


class DomainService:
    """Service for managing domain groups and related operations."""

    def __init__(self, db: Session):
        self.db = db

    # Domain Group CRUD Operations
    def create_domain_group(
        self,
        domain_data: DomainGroupCreate,
        current_user: User,
    ) -> DomainGroup:
        """Create a new domain group."""
        # Check permissions
        if not self._can_create_domain_group(current_user):
            raise PermissionDeniedError(
                "Insufficient permissions to create domain groups",
            )

        # Validate parent domain if specified
        if domain_data.parent_domain_id:
            parent_domain = self.get_domain_group_by_id(
                domain_data.parent_domain_id,
                current_user,
            )
            if not parent_domain:
                raise DomainGroupNotFoundError("Parent domain group not found")

            # Check if user can create child domains
            if not self._can_manage_domain_group(parent_domain, current_user):
                raise PermissionDeniedError(
                    "Cannot create domain group under this parent",
                )

        # Create domain group
        domain_group = DomainGroup(
            name=domain_data.name,
            description=domain_data.description,
            display_name=domain_data.display_name,
            domain_type=domain_data.domain_type,
            parent_domain_id=domain_data.parent_domain_id,
            organization_id=domain_data.organization_id or current_user.organization_id,
            external_id=domain_data.external_id,
            tags=domain_data.tags,
            is_public=domain_data.is_public,
            default_access_level=domain_data.default_access_level,
            allow_self_join=domain_data.allow_self_join,
            require_approval=domain_data.require_approval,
            settings=domain_data.settings,
            permissions=domain_data.permissions,
        )

        self.db.add(domain_group)
        self.db.commit()
        self.db.refresh(domain_group)

        # Add creator as owner
        self._add_domain_member(
            domain_group.id,
            current_user.id,
            AccessLevel.OWNER,
            current_user.id,
        )

        # Log activity
        self._log_domain_activity(
            domain_group.id,
            current_user.id,
            "domain_created",
            description=f"Domain group '{domain_data.name}' created",
        )

        return domain_group

    def get_domain_group_by_id(
        self,
        domain_id: str,
        current_user: User,
    ) -> DomainGroup | None:
        """Get domain group by ID with permission check."""
        domain_group = (
            self.db.query(DomainGroup)
            .options(joinedload(DomainGroup.members))
            .options(joinedload(DomainGroup.resources))
            .filter(DomainGroup.id == domain_id)
            .first()
        )

        if not domain_group:
            return None

        # Check access permissions
        if not self._can_access_domain_group(domain_group, current_user):
            raise PermissionDeniedError("Access denied to this domain group")

        return domain_group

    def list_domain_groups(
        self,
        search_params: DomainSearchParams,
        current_user: User,
    ) -> dict[str, Any]:
        """List domain groups with filtering and pagination."""
        query = self.db.query(DomainGroup)

        # Apply filters
        if search_params.query:
            query = query.filter(
                or_(
                    DomainGroup.name.ilike(f"%{search_params.query}%"),
                    DomainGroup.description.ilike(f"%{search_params.query}%"),
                ),
            )

        if search_params.domain_type:
            query = query.filter(DomainGroup.domain_type == search_params.domain_type)

        if search_params.organization_id:
            query = query.filter(
                DomainGroup.organization_id == search_params.organization_id,
            )
        elif current_user.organization_id:
            # Filter by user's organization if not super admin
            if current_user.role not in [UserRole.SUPER_ADMIN]:
                query = query.filter(
                    DomainGroup.organization_id == current_user.organization_id,
                )

        if search_params.parent_domain_id:
            query = query.filter(
                DomainGroup.parent_domain_id == search_params.parent_domain_id,
            )

        if search_params.is_public is not None:
            query = query.filter(DomainGroup.is_public == search_params.is_public)

        if search_params.is_active is not None:
            query = query.filter(DomainGroup.is_active == search_params.is_active)

        if search_params.tags:
            for tag in search_params.tags:
                query = query.filter(DomainGroup.tags.contains([tag]))

        if search_params.created_after:
            query = query.filter(DomainGroup.created_at >= search_params.created_after)

        if search_params.created_before:
            query = query.filter(DomainGroup.created_at <= search_params.created_before)

        # Apply access control
        if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            # Users can only see domains they're members of or public domains
            query = query.filter(
                or_(
                    DomainGroup.is_public,
                    DomainGroup.members.any(id=current_user.id),
                ),
            )

        # Count total
        total = query.count()

        # Apply pagination
        offset = (search_params.page - 1) * search_params.size
        domains = query.offset(offset).limit(search_params.size).all()

        return {
            "domains": domains,
            "total": total,
            "page": search_params.page,
            "size": search_params.size,
            "pages": (total + search_params.size - 1) // search_params.size,
        }

    def update_domain_group(
        self,
        domain_id: str,
        domain_data: DomainGroupUpdate,
        current_user: User,
    ) -> DomainGroup:
        """Update domain group."""
        domain_group = self.get_domain_group_by_id(domain_id, current_user)
        if not domain_group:
            raise DomainGroupNotFoundError("Domain group not found")

        # Check management permissions
        if not self._can_manage_domain_group(domain_group, current_user):
            raise PermissionDeniedError("Cannot modify this domain group")

        # Update fields
        update_data = domain_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(domain_group, field, value)

        domain_group.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(domain_group)

        # Log activity
        self._log_domain_activity(
            domain_group.id,
            current_user.id,
            "domain_updated",
            description=f"Domain group '{domain_group.name}' updated",
        )

        return domain_group

    def delete_domain_group(
        self,
        domain_id: str,
        current_user: User,
    ) -> bool:
        """Delete domain group."""
        domain_group = self.get_domain_group_by_id(domain_id, current_user)
        if not domain_group:
            raise DomainGroupNotFoundError("Domain group not found")

        # Check management permissions
        if not self._can_manage_domain_group(domain_group, current_user):
            raise PermissionDeniedError("Cannot delete this domain group")

        # Check if domain has child domains
        child_domains = (
            self.db.query(DomainGroup)
            .filter(DomainGroup.parent_domain_id == domain_id)
            .count()
        )

        if child_domains > 0:
            raise PermissionDeniedError("Cannot delete domain group with child domains")

        # Log activity before deletion
        self._log_domain_activity(
            domain_group.id,
            current_user.id,
            "domain_deleted",
            description=f"Domain group '{domain_group.name}' deleted",
        )

        # Delete domain group
        self.db.delete(domain_group)
        self.db.commit()

        return True

    # Member Management
    def add_domain_member(
        self,
        domain_id: str,
        member_data: DomainMemberCreate,
        current_user: User,
    ) -> bool:
        """Add member to domain group."""
        domain_group = self.get_domain_group_by_id(domain_id, current_user)
        if not domain_group:
            raise DomainGroupNotFoundError("Domain group not found")

        # Check if user can manage members
        if not self._can_manage_domain_members(domain_group, current_user):
            raise PermissionDeniedError("Cannot manage members in this domain group")

        # Check if user exists
        user = self.db.query(User).filter(User.id == member_data.user_id).first()
        if not user:
            raise UserNotFoundError("User not found")

        # Check if user is already a member
        existing_member = domain_group.members.filter_by(id=member_data.user_id).first()
        if existing_member:
            raise PermissionDeniedError("User is already a member of this domain group")

        # Add member
        return self._add_domain_member(
            domain_id,
            member_data.user_id,
            member_data.access_level,
            member_data.invited_by or current_user.id,
        )

    def update_domain_member(
        self,
        domain_id: str,
        user_id: str,
        member_data: DomainMemberUpdate,
        current_user: User,
    ) -> bool:
        """Update domain member."""
        domain_group = self.get_domain_group_by_id(domain_id, current_user)
        if not domain_group:
            raise DomainGroupNotFoundError("Domain group not found")

        # Check if user can manage members
        if not self._can_manage_domain_members(domain_group, current_user):
            raise PermissionDeniedError("Cannot manage members in this domain group")

        # Update member access level
        member = domain_group.members.filter_by(id=user_id).first()
        if not member:
            raise UserNotFoundError("User is not a member of this domain group")

        update_data = member_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(member, field, value)

        self.db.commit()

        # Log activity
        self._log_domain_activity(
            domain_id,
            current_user.id,
            "member_updated",
            description=f"Member access level updated for user {user_id}",
        )

        return True

    def remove_domain_member(
        self,
        domain_id: str,
        user_id: str,
        current_user: User,
    ) -> bool:
        """Remove member from domain group."""
        domain_group = self.get_domain_group_by_id(domain_id, current_user)
        if not domain_group:
            raise DomainGroupNotFoundError("Domain group not found")

        # Check if user can manage members
        if not self._can_manage_domain_members(domain_group, current_user):
            raise PermissionDeniedError("Cannot manage members in this domain group")

        # Remove member
        member = domain_group.members.filter_by(id=user_id).first()
        if not member:
            raise UserNotFoundError("User is not a member of this domain group")

        domain_group.members.remove(member)
        self.db.commit()

        # Log activity
        self._log_domain_activity(
            domain_id,
            current_user.id,
            "member_removed",
            description=f"Member removed: {user_id}",
        )

        return True

    # Resource Management
    def add_domain_resource(
        self,
        domain_id: str,
        resource_data: DomainResourceCreate,
        current_user: User,
    ) -> DomainResource:
        """Add resource to domain group."""
        domain_group = self.get_domain_group_by_id(domain_id, current_user)
        if not domain_group:
            raise DomainGroupNotFoundError("Domain group not found")

        # Check if user can manage resources
        if not self._can_manage_domain_resources(domain_group, current_user):
            raise PermissionDeniedError("Cannot manage resources in this domain group")

        # Create domain resource
        domain_resource = DomainResource(
            domain_group_id=domain_id,
            resource_id=resource_data.resource_id,
            resource_type=resource_data.resource_type,
            resource_name=resource_data.resource_name,
            access_level=resource_data.access_level,
            is_public=resource_data.is_public,
            description=resource_data.description,
            tags=resource_data.tags,
            metadata=resource_data.metadata,
            added_by=resource_data.added_by or current_user.id,
        )

        self.db.add(domain_resource)
        self.db.commit()
        self.db.refresh(domain_resource)

        # Log activity
        self._log_domain_activity(
            domain_id,
            current_user.id,
            "resource_added",
            resource_type=resource_data.resource_type,
            resource_id=resource_data.resource_id,
            description=f"Resource added: {resource_data.resource_name or resource_data.resource_id}",
        )

        return domain_resource

    def update_domain_resource(
        self,
        domain_id: str,
        resource_id: str,
        resource_data: DomainResourceUpdate,
        current_user: User,
    ) -> DomainResource:
        """Update domain resource."""
        domain_group = self.get_domain_group_by_id(domain_id, current_user)
        if not domain_group:
            raise DomainGroupNotFoundError("Domain group not found")

        # Check if user can manage resources
        if not self._can_manage_domain_resources(domain_group, current_user):
            raise PermissionDeniedError("Cannot manage resources in this domain group")

        # Find resource
        resource = (
            self.db.query(DomainResource)
            .filter(
                and_(
                    DomainResource.domain_group_id == domain_id,
                    DomainResource.resource_id == resource_id,
                    DomainResource.is_active,
                ),
            )
            .first()
        )

        if not resource:
            raise ResourceNotFoundError("Resource not found in domain group")

        # Update resource
        update_data = resource_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(resource, field, value)

        resource.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(resource)

        # Log activity
        self._log_domain_activity(
            domain_id,
            current_user.id,
            "resource_updated",
            resource_type=resource.resource_type,
            resource_id=resource.resource_id,
            description=f"Resource updated: {resource.resource_name or resource.resource_id}",
        )

        return resource

    def remove_domain_resource(
        self,
        domain_id: str,
        resource_id: str,
        current_user: User,
    ) -> bool:
        """Remove resource from domain group."""
        domain_group = self.get_domain_group_by_id(domain_id, current_user)
        if not domain_group:
            raise DomainGroupNotFoundError("Domain group not found")

        # Check if user can manage resources
        if not self._can_manage_domain_resources(domain_group, current_user):
            raise PermissionDeniedError("Cannot manage resources in this domain group")

        # Find and deactivate resource
        resource = (
            self.db.query(DomainResource)
            .filter(
                and_(
                    DomainResource.domain_group_id == domain_id,
                    DomainResource.resource_id == resource_id,
                    DomainResource.is_active,
                ),
            )
            .first()
        )

        if not resource:
            raise ResourceNotFoundError("Resource not found in domain group")

        resource.is_active = False
        self.db.commit()

        # Log activity
        self._log_domain_activity(
            domain_id,
            current_user.id,
            "resource_removed",
            resource_type=resource.resource_type,
            resource_id=resource.resource_id,
            description=f"Resource removed: {resource.resource_name or resource.resource_id}",
        )

        return True

    # Invitation Management
    def create_domain_invitation(
        self,
        domain_id: str,
        invitation_data: DomainInvitationCreate,
        current_user: User,
    ) -> DomainInvitation:
        """Create domain invitation."""
        domain_group = self.get_domain_group_by_id(domain_id, current_user)
        if not domain_group:
            raise DomainGroupNotFoundError("Domain group not found")

        # Check if user can invite members
        if not self._can_manage_domain_members(domain_group, current_user):
            raise PermissionDeniedError("Cannot invite members to this domain group")

        # Generate invitation token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=invitation_data.expires_in_days)

        # Create invitation
        invitation = DomainInvitation(
            domain_group_id=domain_id,
            email=invitation_data.email,
            access_level=invitation_data.access_level,
            message=invitation_data.message,
            token=token,
            expires_at=expires_at,
        )

        self.db.add(invitation)
        self.db.commit()
        self.db.refresh(invitation)

        # Log activity
        self._log_domain_activity(
            domain_id,
            current_user.id,
            "invitation_created",
            description=f"Invitation sent to {invitation_data.email}",
        )

        return invitation

    def accept_domain_invitation(
        self,
        token: str,
        current_user: User,
    ) -> bool:
        """Accept domain invitation."""
        invitation = (
            self.db.query(DomainInvitation)
            .filter(
                and_(
                    DomainInvitation.token == token,
                    DomainInvitation.status == "pending",
                    DomainInvitation.expires_at > datetime.now(),
                ),
            )
            .first()
        )

        if not invitation:
            raise InvitationNotFoundError("Invalid or expired invitation")

        # Check if user is already a member
        domain_group = self.get_domain_group_by_id(
            str(invitation.domain_group_id),
            current_user,
        )
        if domain_group.members.filter_by(id=current_user.id).first():
            raise PermissionDeniedError("User is already a member of this domain group")

        # Add user as member
        self._add_domain_member(
            str(invitation.domain_group_id),
            current_user.id,
            invitation.access_level,
            None,  # No invited_by for self-acceptance
        )

        # Update invitation status
        invitation.status = "accepted"
        invitation.accepted_at = datetime.now()
        invitation.user_id = current_user.id
        self.db.commit()

        # Log activity
        self._log_domain_activity(
            str(invitation.domain_group_id),
            current_user.id,
            "invitation_accepted",
            description=f"Invitation accepted by {current_user.email}",
        )

        return True

    # Statistics and Analytics
    def get_domain_stats(
        self,
        organization_id: str | None = None,
        current_user: User = None,
    ) -> DomainGroupStats:
        """Get domain group statistics."""
        query = self.db.query(DomainGroup)

        # Filter by organization
        if organization_id:
            query = query.filter(DomainGroup.organization_id == organization_id)
        elif current_user and current_user.organization_id:
            query = query.filter(
                DomainGroup.organization_id == current_user.organization_id,
            )

        # Apply access control
        if current_user and current_user.role not in [
            UserRole.SUPER_ADMIN,
            UserRole.ADMIN,
        ]:
            query = query.filter(
                or_(
                    DomainGroup.is_public,
                    DomainGroup.members.any(id=current_user.id),
                ),
            )

        total_domains = query.count()
        active_domains = query.filter(DomainGroup.is_active).count()

        # Get member and resource counts
        total_members = self.db.query(func.count(DomainGroup.members)).scalar()
        total_resources = self.db.query(func.count(DomainResource.id)).scalar()

        # Get domains by type
        domains_by_type = {}
        for domain_type in DomainType:
            count = query.filter(DomainGroup.domain_type == domain_type).count()
            if count > 0:
                domains_by_type[domain_type] = count

        # Get recent activities (last 7 days)
        recent_activities = (
            self.db.query(DomainActivity)
            .filter(DomainActivity.created_at >= datetime.now() - timedelta(days=7))
            .count()
        )

        # Get pending invitations
        pending_invitations = (
            self.db.query(DomainInvitation)
            .filter(
                and_(
                    DomainInvitation.status == "pending",
                    DomainInvitation.expires_at > datetime.now(),
                ),
            )
            .count()
        )

        return DomainGroupStats(
            total_domains=total_domains,
            active_domains=active_domains,
            total_members=total_members,
            total_resources=total_resources,
            domains_by_type=domains_by_type,
            recent_activities=recent_activities,
            pending_invitations=pending_invitations,
        )

    # Helper Methods
    def _add_domain_member(
        self,
        domain_id: str,
        user_id: str,
        access_level: AccessLevel,
        invited_by: str | None,
    ) -> bool:
        """Internal method to add domain member."""
        # This would use the association table directly
        # For now, we'll use the relationship
        domain_group = (
            self.db.query(DomainGroup).filter(DomainGroup.id == domain_id).first()
        )
        user = self.db.query(User).filter(User.id == user_id).first()

        if domain_group and user:
            domain_group.members.append(user)
            self.db.commit()
            return True
        return False

    def _can_create_domain_group(self, user: User) -> bool:
        """Check if user can create domain groups."""
        return user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER]

    def _can_access_domain_group(self, domain_group: DomainGroup, user: User) -> bool:
        """Check if user can access domain group."""
        # Super admins can access all domains
        if user.role == UserRole.SUPER_ADMIN:
            return True

        # Public domains are accessible to all
        if domain_group.is_public:
            return True

        # Check if user is a member
        if domain_group.members.filter_by(id=user.id).first():
            return True

        # Organization admins can access domains in their organization
        return bool(user.role == UserRole.ADMIN and domain_group.organization_id == user.organization_id)

    def _can_manage_domain_group(self, domain_group: DomainGroup, user: User) -> bool:
        """Check if user can manage domain group."""
        # Super admins can manage all domains
        if user.role == UserRole.SUPER_ADMIN:
            return True

        # Check if user is an owner or admin of the domain
        member = domain_group.members.filter_by(id=user.id).first()
        if member and member.access_level in [AccessLevel.ADMIN, AccessLevel.OWNER]:
            return True

        # Organization admins can manage domains in their organization
        return bool(user.role == UserRole.ADMIN and domain_group.organization_id == user.organization_id)

    def _can_manage_domain_members(self, domain_group: DomainGroup, user: User) -> bool:
        """Check if user can manage domain members."""
        return self._can_manage_domain_group(domain_group, user)

    def _can_manage_domain_resources(
        self,
        domain_group: DomainGroup,
        user: User,
    ) -> bool:
        """Check if user can manage domain resources."""
        return self._can_manage_domain_group(domain_group, user)

    def _log_domain_activity(
        self,
        domain_id: str,
        user_id: str,
        activity_type: str,
        resource_type: ResourceType | None = None,
        resource_id: str | None = None,
        description: str = "",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Log domain activity."""
        activity = DomainActivity(
            domain_group_id=domain_id,
            user_id=user_id,
            activity_type=activity_type,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            details=details,
        )

        self.db.add(activity)
        self.db.commit()
