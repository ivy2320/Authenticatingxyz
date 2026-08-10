from pydantic import BaseModel, EmailStr
from typing import Optional

# Request schemas (what the client sends)
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Response schemas (what the server sends back)
class UserResponse(BaseModel):
    id: str
    email: str
    is_verified: bool
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MessageResponse(BaseModel):
    message: str