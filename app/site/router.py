from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import FileResponse

# app/site/router.py -> app/site -> app -> racine du projet
BASE = Path(__file__).resolve().parent.parent.parent
PUBLIC_INDEX = BASE / "frontend" / "public" / "index.html"

router = APIRouter(tags=["site"])

@router.get("/")
def public_site():
    """
    Vitrine publique (accueil, carte, formules, approche, fonctionnement,
    qui sommes-nous, contact). Contenu 100% public : aucune session,
    aucun secret, aucune règle métier. Ce module ne doit JAMAIS importer
    quoi que ce soit depuis auth/, client_app/ ou admin_app/.
    """
    return FileResponse(PUBLIC_INDEX, media_type="text/html")
