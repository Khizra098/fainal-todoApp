"""
Authentication middleware for the verification system.
This module provides authentication and authorization functionality.
"""

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from ..models.user import UserInDB
from ..services.user_service import UserService
from ..database.database import get_db
from sqlalchemy.orm import Session


# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


class JWTBearer(HTTPBearer):
    """
    JWT Bearer authentication scheme
    """
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            token = credentials.credentials
            user = self.verify_jwt(token)
            if not user:
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            request.state.user = user
            return token
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> Optional[dict]:
        """
        Verify JWT token and return user payload
        """
        try:
            payload = jwt.decode(jwtoken, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a new access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> UserInDB:
    """
    Get current authenticated user from request
    """
    token = request.headers.get("authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = token[7:]  # Remove "Bearer " prefix

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_service = UserService(db)
    user = user_service.get_user_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_user_role(user: UserInDB) -> str:
    """
    Get user role from user object
    """
    # This is a simplified role system - in production, you'd have a proper role system
    # For now, we'll just return a default role
    return "user"


def require_role(required_role: str):
    """
    Decorator to require a specific role for accessing a route
    """
    def role_checker(current_user: UserInDB = Depends(get_current_user)):
        user_role = get_user_role(current_user)
        if user_role != required_role:
            raise HTTPException(
                status_code=403,
                detail=f"Operation not permitted. Required role: {required_role}, got: {user_role}",
            )
        return current_user
    return role_checker