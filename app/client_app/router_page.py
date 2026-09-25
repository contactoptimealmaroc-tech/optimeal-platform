from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from ..core.page_guard import require_page_role

TEMPLATE = Path(__file__).resolve().parent / "templates" / "client.html"

router = APIRouter(tags=["client-page"])

@router.get("/client")
def client_page(request: Request):
    denied = require_page_role(request, "CLIENT")
    if denied:
        return denied
    return FileResponse(TEMPLATE, media_type="text/html")
