from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..schemas import ApiResponse, ApiError, UserCreate, LoginRequest
from .. import models
from ..db import get_db
from ..auth import get_password_hash, create_access_token, authenticate_user, get_current_user, revoke_token
from ..config import settings

router = APIRouter()

@router.post("/register", response_model=ApiResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    # validate password strength
    if len(payload.password) < 8:
        return ApiResponse(success=False, data=None, error=ApiError(code="INVALID_PAYLOAD", message="Password too weak", details=None))
    normalized_email = payload.email.lower()
    existing = db.query(models.User).filter(models.User.email == normalized_email).first()
    if existing:
        return ApiResponse(success=False, data=None, error=ApiError(code="USER_EXISTS", message="User already exists", details=None))
    hashed = get_password_hash(payload.password)
    user = models.User(name=payload.name.strip(), email=normalized_email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id)
    data = {"user": {"id": user.id, "name": user.name, "email": user.email, "created_at": user.created_at.isoformat()}, "access_token": token, "token_type": "bearer", "expires_in": settings.access_token_expire_minutes*60}
    return ApiResponse(success=True, data=data, error=None)


@router.post("/login", response_model=ApiResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        # Generic error to avoid user enumeration
        return ApiResponse(success=False, data=None, error=ApiError(code="INVALID_CREDENTIALS", message="Invalid credentials", details=None))
    token = create_access_token(user.id)
    data = {"user": {"id": user.id, "name": user.name, "email": user.email}, "access_token": token, "token_type": "bearer", "expires_in": settings.access_token_expire_minutes*60}
    return ApiResponse(success=True, data=data, error=None)


@router.get("/me", response_model=ApiResponse)
def me(current_user: models.User = Depends(get_current_user)):
    data = {"user": {"id": current_user.id, "name": current_user.name, "email": current_user.email, "created_at": current_user.created_at.isoformat()}}
    return ApiResponse(success=True, data=data, error=None)


@router.post("/logout", response_model=ApiResponse)
def logout(request: Request, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Expect Authorization header
    auth = request.headers.get("authorization")
    if not auth:
        return ApiResponse(success=False, data=None, error=ApiError(code="UNAUTHORIZED", message="Missing token", details=None))
    parts = auth.split()
    if len(parts) != 2:
        return ApiResponse(success=False, data=None, error=ApiError(code="INVALID_PAYLOAD", message="Invalid Authorization header", details=None))
    token = parts[1]
    revoked = revoke_token(db, token)
    if not revoked:
        return ApiResponse(success=False, data=None, error=ApiError(code="INFERENCE_ERROR", message="Failed to revoke token", details=None))
    return ApiResponse(success=True, data={"message": "Logged out"}, error=None)
