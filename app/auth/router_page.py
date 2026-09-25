from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, RedirectResponse
from ..core.page_guard import current_page_user

TEMPLATE = Path(__file__).resolve().parent / "templates" / "connexion.html"

router = APIRouter(tags=["auth-page"])

@router.get("/connexion")
def connexion_page(request: Request):
    user = current_page_user(request)
    if user:
        target = "/os" if user.role in ("ADMIN", "CHEF", "NUTRITION") else "/client"
        return RedirectResponse(url=target, status_code=303)
    return FileResponse(TEMPLATE, media_type="text/html")
