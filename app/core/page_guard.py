"""
Avant V27 : les pages /client et /os étaient renvoyées à n'importe qui,
et c'est le JavaScript qui découvrait après-coup (401 de l'API) qu'il fallait
rediriger vers /connexion. La page (coquille HTML vide de logique) restait donc
techniquement récupérable sans être connecté.

Ici, le contrôle se fait AVANT d'envoyer le moindre octet de HTML : si la session
est absente ou invalide, ou si le rôle ne correspond pas, on redirige côté serveur.
Le principe reste le même que pour l'API (core.security), mais sans lever
d'exception JSON puisqu'on répond à un navigateur, pas à un fetch().
"""
from typing import Optional
from fastapi import Request
from fastapi.responses import RedirectResponse
from .db import SessionLocal
from .security import get_session_user
from .models import User

def current_page_user(request: Request) -> Optional[User]:
    db = SessionLocal()
    try:
        return get_session_user(request, db)
    finally:
        db.close()

def require_page_role(request: Request, *roles: str) -> Optional[RedirectResponse]:
    """Retourne une redirection vers /connexion si l'accès n'est pas autorisé, sinon None."""
    user = current_page_user(request)
    if not user or (roles and user.role not in roles):
        return RedirectResponse(url="/connexion", status_code=303)
    return None
