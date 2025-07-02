"""User service for managing users."""

from typing import List, Optional
from sqlalchemy.orm import Session


class UserService:
    """Service for managing users."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID."""
        return {"message": "User service - to be implemented"}
    
    def get_all_users(self) -> List:
        """Get all users."""
        return [] 