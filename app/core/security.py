from datetime import datetime, timedelta, timezone
from typing import Optional
import base64, hashlib, hmac, os
import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db
from .models import User

ALGORITHM = "HS256"
ITERATIONS = 600_000

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"

def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, it, salt_b64, digest_b64 = stored.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(digest_b64.encode())
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(it))
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False

def make_session_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user.id), "role": user.role, "iat": now, "exp": now + timedelta(seconds=settings.session_max_age)}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)

def _extract_token(request: Request) -> Optional[str]:
    token = request.cookies.get(settings.session_cookie)
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
    return token

def _decode(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except Exception:
        return None

def current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Dépendance API JSON : lève 401 si la session est absente/invalide. Ne jamais utiliser pour servir une page HTML (voir page_guard)."""
    token = _extract_token(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="AUTH_REQUIRED")
    payload = _decode(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_SESSION")
    user = db.get(User, int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="USER_INACTIVE")
    return user

def get_session_user(request: Request, db: Session) -> Optional[User]:
    """Variante non-bloquante (ne lève jamais) : renvoie None si pas de session valide. Réservée aux routes de PAGE (redirection), jamais aux routes API JSON."""
    token = _extract_token(request)
    if not token:
        return None
    payload = _decode(token)
    if not payload:
        return None
    user = db.get(User, int(payload["sub"]))
    if not user or not user.is_active:
        return None
    return user

def require_roles(*roles):
    def dep(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
        return user
    return dep
