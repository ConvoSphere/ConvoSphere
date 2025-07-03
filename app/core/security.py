from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> "User":
    """
    Get current user from JWT token.
    """
 