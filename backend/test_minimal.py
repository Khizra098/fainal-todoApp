from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
import jwt
from datetime import datetime, timedelta
import os

# Define the same models and configurations as in auth_routes.py
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

app = FastAPI()

@app.put("/auth/profile", response_model=UserResponse)
def update_profile_test(request: UpdateProfileRequest):
    """Test endpoint to see if the basic structure works."""
    # Return mock data
    return UserResponse(id=1, name=request.name or "Test Name", email=request.email or "test@example.com")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)