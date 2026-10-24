from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.core.database import get_db
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.models.user import User
from backend.app.models.profile import CandidateProfile
from backend.app.api.deps import get_current_user
from backend.app.services.audit_service import log_audit_event

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    preferred_role: str = "Full Stack Developer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
        
    result = await db.execute(select(User).where(User.email == req.email.lower()))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email is already registered. Please log in.")
        
    user = User(
        email=req.email.lower(),
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name,
        role="candidate"
    )
    db.add(user)
    await db.flush()

    # Create associated profile
    profile = CandidateProfile(
        user_id=user.id,
        headline=f"Aspiring {req.preferred_role}",
        preferred_role=req.preferred_role,
        summary="Passionate technologist eager to apply verified skills and hands-on projects to high-impact career opportunities."
    )
    db.add(profile)
    await db.commit()
    await db.refresh(user)

    await log_audit_event(db, user.id, "user_registered", {"email": user.email})

    token = create_access_token(user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email.lower()))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    token = create_access_token(user.id)
    await log_audit_event(db, user.id, "user_login", {"email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    prof_res = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
    profile = prof_res.scalar_one_or_none()
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "profile": {
            "id": profile.id if profile else None,
            "headline": profile.headline if profile else "",
            "summary": profile.summary if profile else "",
            "preferred_role": profile.preferred_role if profile else "",
            "work_arrangement": profile.work_arrangement if profile else "remote",
        } if profile else None
    }
