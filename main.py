from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import User, RefreshToken
from schemas import RegisterRequest, LoginRequest, UserResponse, TokenResponse, MessageResponse
from security import hash_password, verify_password, create_access_token, decode_access_token, generate_refresh_token, hash_refresh_token
from datetime import datetime, timedelta
import os

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Platform", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5500" , "https://authenticatingxyz-frontend.onrender.com/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REFRESH_TOKEN_COOKIE_NAME = "refresh_token"

@app.get("/")
def root():
    return {"status": "ok", "service": "auth-platform"}

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Unable to register with these details")
    
    # Hash password and create user
    hashed_password = hash_password(payload.password)
    new_user = User(email=payload.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Issue refresh token and set as httpOnly cookie
    refresh_token_raw = generate_refresh_token()
    refresh_token_hash = hash_refresh_token(refresh_token_raw)
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    db_refresh_token = RefreshToken(
        token_hash=refresh_token_hash,
        user_id=new_user.id,
        expires_at=expires_at
    )
    db.add(db_refresh_token)
    db.commit()
    
    # Set httpOnly cookie
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token_raw,
        httponly=True,
        secure= True, 
        samesite="strict",
        max_age=7 * 24 * 60 * 60,  # 7 days
    )
    
    return new_user

@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(User).filter(User.email == payload.email).first()
    
    # Generic error message
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create access token
    access_token = create_access_token(user.id)
    
    # Generate refresh token
    refresh_token_raw = generate_refresh_token()
    refresh_token_hash = hash_refresh_token(refresh_token_raw)
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    db_refresh_token = RefreshToken(
        token_hash=refresh_token_hash,
        user_id=user.id,
        expires_at=expires_at
    )
    db.add(db_refresh_token)
    db.commit()
    
    # Set httpOnly cookie
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token_raw,
        httponly=True,
        secure=False,  # Set to True in production (requires HTTPS)
        samesite="strict",
        max_age=7 * 24 * 60 * 60,
    )
    
    return TokenResponse(access_token=access_token)

@app.post("/auth/refresh", response_model=TokenResponse)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    # Read refresh token from httpOnly cookie
    refresh_token_raw = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    
    if not refresh_token_raw:
        raise HTTPException(status_code=401, detail="No refresh token provided")
    
    # Hash and look up in DB
    refresh_token_hash = hash_refresh_token(refresh_token_raw)
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == refresh_token_hash
    ).first()
    
    if not db_token or db_token.revoked or db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    # Revoke old token
    db_token.revoked = True
    db.commit()
    
    # Issue new access token
    access_token = create_access_token(db_token.user_id)
    
    # Generate and store new refresh token
    new_refresh_token_raw = generate_refresh_token()
    new_refresh_token_hash = hash_refresh_token(new_refresh_token_raw)
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    new_db_token = RefreshToken(
        token_hash=new_refresh_token_hash,
        user_id=db_token.user_id,
        expires_at=expires_at
    )
    db.add(new_db_token)
    db.commit()
    
    # Set new httpOnly cookie
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=new_refresh_token_raw,
        httponly=True,
        secure=False,
        samesite="strict",
        max_age=7 * 24 * 60 * 60,
    )
    
    return TokenResponse(access_token=access_token)

@app.post("/auth/logout", response_model=MessageResponse)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    # Read refresh token from cookie
    refresh_token_raw = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    
    if refresh_token_raw:
        # Mark as revoked in DB
        refresh_token_hash = hash_refresh_token(refresh_token_raw)
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == refresh_token_hash
        ).first()
        
        if db_token:
            db_token.revoked = True
            db.commit()
    
    # Clear cookie
    response.delete_cookie(REFRESH_TOKEN_COOKIE_NAME)
    
    return MessageResponse(message="Logged out successfully")

@app.get("/auth/me", response_model=UserResponse)
def get_current_user(request: Request, db: Session = Depends(get_db)):
    # Read JWT from Authorization header
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")
    
    token = auth_header.split(" ")[1]
    user_id = decode_access_token(token)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user