from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .config import settings
from . import models
from .db import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {
        "sub": str(subject),
        "exp": int(expire.timestamp()),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])

def revoke_token(db: Session, token: str) -> bool:
    try:
        payload = decode_token(token)
        jti = payload.get("jti")
        if not jti:
            return False
        expires_at = datetime.fromtimestamp(payload["exp"], timezone.utc)
        db.add(models.RevokedToken(id=str(uuid.uuid4()), jti=jti, expires_at=expires_at))
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False

def is_token_revoked(db: Session, token: str) -> bool:
    try:
        payload = decode_token(token)
        jti = payload.get("jti")
        if not jti:
            return True
        return db.query(models.RevokedToken).filter(models.RevokedToken.jti == jti).first() is not None
    except Exception:
        return True

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = db.query(models.User).filter(models.User.email == email.lower()).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = decode_token(token).get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if is_token_revoked(db, token):
        raise HTTPException(status_code=401, detail="Token revoked or invalid")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise credentials_exception
    return user

def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user
