"""Authentication endpoints for the Todo Chatbot API."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from ...database import get_db
from ...models.user import User
from ...services.user_service import UserService
from pydantic import BaseModel
import hashlib
import os
import secrets
from ...auth.auth_handler import verify_password, get_password_hash

router = APIRouter(prefix="/auth", tags=["authentication"])

# OAuth2 scheme for JWT token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secret key for JWT - in production, use a strong secret from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    token: str
    user_id: int
    email: str


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    theme: str = "light"
    language: str = "en"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    two_factor_enabled: bool = False


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ChangePasswordResponse(BaseModel):
    success: bool
    message: str


class ToggleTwoFactorRequest(BaseModel):
    enable: bool


class UpdatePreferencesRequest(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None


class TwoFactorResponse(BaseModel):
    success: bool
    qr_code_url: Optional[str] = None
    secret: Optional[str] = None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=TokenResponse)
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    user_service = UserService(db)

    # Check if user already exists
    existing_user = user_service.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Hash the password using bcrypt
    hashed_password = get_password_hash(request.password)

    # Create the user
    user = user_service.create_user(
        name=request.name,
        email=request.email,
        password_hash=hashed_password
    )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "user_id": user.id
    }
    token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )

    return TokenResponse(
        token=token,
        user_id=user.id,
        email=user.email
    )


@router.put("/profile", response_model=UserResponse)
def update_profile(
    request: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user profile information."""
    user_service = UserService(db)

    # Check if email is being changed and if it's already taken by another user
    if request.email and request.email != current_user.email:
        existing_user = user_service.get_user_by_email(request.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered with another account"
            )

    # Update user profile
    updated_user = user_service.update_user(
        user_id=current_user.id,
        name=request.name or current_user.name,
        email=request.email or current_user.email
    )

    return updated_user


@router.get("/me", response_model=UserResponse)
def get_current_user_details(
    current_user: User = Depends(get_current_user)
):
    """Get current user details including theme and language preferences."""
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        theme=current_user.theme,
        language=current_user.language,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        two_factor_enabled=current_user.two_factor_enabled
    )


@router.put("/preferences", response_model=UserResponse)
def update_preferences(
    request: UpdatePreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences including theme and language."""
    user_service = UserService(db)

    # Update user preferences
    updated_user = user_service.update_user(
        user_id=current_user.id,
        theme=request.theme or current_user.theme,
        language=request.language or current_user.language
    )

    return UserResponse(
        id=updated_user.id,
        name=updated_user.name,
        email=updated_user.email,
        theme=updated_user.theme,
        language=updated_user.language,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
        two_factor_enabled=updated_user.two_factor_enabled
    )


@router.post("/login", response_model=TokenResponse)
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user_service = UserService(db)

    # Find user by email
    user = user_service.get_user_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "user_id": user.id
    }
    token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )

    return TokenResponse(
        token=token,
        user_id=user.id,
        email=user.email
    )


@router.put("/change-password", response_model=ChangePasswordResponse)
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password."""
    user_service = UserService(db)

    # Validate new password length
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters"
        )

    # Additional password complexity validation
    if not any(c.isupper() for c in request.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must contain at least one uppercase letter"
        )

    if not any(c.islower() for c in request.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must contain at least one lowercase letter"
        )

    if not any(c.isdigit() for c in request.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must contain at least one digit"
        )

    # Validate that new password is not the same as current password
    if request.new_password == request.current_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as current password"
        )

    success = user_service.change_password(
        user_id=current_user.id,
        current_password=request.current_password,
        new_password=request.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    return ChangePasswordResponse(success=True, message="Password changed successfully")


@router.post("/toggle-two-factor", response_model=TwoFactorResponse)
def toggle_two_factor(
    request: ToggleTwoFactorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle two-factor authentication for user."""
    user_service = UserService(db)

    if request.enable and not current_user.two_factor_secret:
        # Setup 2FA if not already configured
        secret, totp_uri = user_service.setup_two_factor(current_user.id)
        return TwoFactorResponse(
            success=True,
            qr_code_url=totp_uri,
            secret=secret
        )
    else:
        # Toggle the 2FA status
        success = user_service.toggle_two_factor(current_user.id, request.enable)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update two-factor authentication settings"
            )

        return TwoFactorResponse(success=True)


@router.post("/logout-all-devices")
def logout_all_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log out user from all devices."""
    # In a real implementation, you would invalidate all tokens for the user
    # For now, we'll just return a success message
    # This could involve maintaining a blacklist of tokens or using a refresh token system

    # In a real app, you'd add the current user's tokens to a blacklist
    # For this implementation, we'll just return success
    return {"success": True, "message": "Logged out from all devices"}