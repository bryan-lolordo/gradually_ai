from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging
from pydantic import BaseModel, EmailStr, constr

from database import get_db_context
from database.models import User
from utils.password import hash_password, verify_password, needs_rehash
from utils.auth import create_access_token, get_token_payload, get_current_user

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Request Models (will move to schemas later)
class RegisterUserRequest(BaseModel):
    username: constr(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: constr(min_length=8, max_length=100)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

@router.get("/me", response_model=UserResponse)
async def get_current_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_context)
):
    """Get current user data."""
    logger.info("🔍 /me endpoint called")
    logger.info(f"👤 Current user ID: {current_user.id}")
    logger.info(f"📧 Current user email: {current_user.email}")
    try:
        return current_user
    except Exception as e:
        logger.error(f"❌ Error in /me endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching user data")

@router.post("/register")
def register_user(request: RegisterUserRequest, db: Session = Depends(get_db_context)):
    """Register a new user."""
    logger.info(f"Registration attempt for email: {request.email}")
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == request.email) | (User.username == request.username)
        ).first()
        
        if existing_user:
            if existing_user.email == request.email:
                logger.warning(f"Email already registered: {request.email}")
                raise HTTPException(status_code=400, detail="Email already registered")
            else:
                logger.warning(f"Username already taken: {request.username}")
                raise HTTPException(status_code=400, detail="Username already taken")
        
        # Hash the password
        try:
            hashed_password = hash_password(request.password)
            logger.info(f"Generated hash length: {len(hashed_password)}")
        except Exception as e:
            logger.error(f"Password hashing error: {str(e)}")
            raise HTTPException(status_code=500, detail="Error processing password")
        
        # Create new user
        try:
            new_user = User(
                username=request.username,
                email=request.email,
                password_hash=hashed_password
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            logger.info(f"User registered successfully with ID: {new_user.id}")
            
            return {
                "id": new_user.id,
                "username": new_user.username
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Database error during user creation: {str(e)}")
            logger.error(f"Full error details: {e.__class__.__name__}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected registration error: {str(e)}")
        logger.error(f"Full error details: {e.__class__.__name__}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/login")
async def login_user(request: LoginRequest, db: Session = Depends(get_db_context)):
    """Authenticate a user and return a JWT token."""
    logger.info(f"Login attempt received for email: {request.email}")
    
    try:
        # Find the user
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            logger.warning(f"No user found with email: {request.email}")
            raise HTTPException(status_code=400, detail="Invalid email or password")
        
        # Verify password
        is_valid = verify_password(request.password, user.password_hash)
        if not is_valid:
            logger.warning("Password verification failed")
            raise HTTPException(status_code=400, detail="Invalid email or password")
        
        # Generate JWT token
        token_payload = get_token_payload(user.id)
        access_token = create_access_token(token_payload)
        
        # Check if password needs rehashing
        if needs_rehash(user.password_hash):
            try:
                user.password_hash = hash_password(request.password)
                db.commit()
                logger.info("✅ Password hash upgraded successfully")
            except Exception as e:
                logger.error(f"Failed to upgrade password hash: {e}")
                db.rollback()
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Login error: {str(e)}")
        logger.error(f"Full error details: {e.__class__.__name__}")
        raise HTTPException(status_code=500, detail="Internal server error") 