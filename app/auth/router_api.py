from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..core.config import settings
from ..core.db import get_db
from ..core.models import User
from ..core.security import make_session_token, verify_password, current_user
from .schemas import LoginIn

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/login")
def login(data: LoginIn, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower().strip()))
    if not user or not user.is_active or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="INVALID_CREDENTIALS")
    token = make_session_token(user)
    response.set_cookie(settings.session_cookie, token, max_age=settings.session_max_age, httponly=True, secure=settings.app_env == "production", samesite="lax", path="/")
    return {"authenticated": True, "role": user.role, "user_id": user.id}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(settings.session_cookie, path="/")
    return {"authenticated": False}

@router.get("/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "email": user.email, "role": user.role}
