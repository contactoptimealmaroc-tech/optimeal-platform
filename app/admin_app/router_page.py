from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from ..core.page_guard import require_page_role

TEMPLATE = Path(__file__).resolve().parent / "templates" / "os.html"
OS_ROLES = ("ADMIN", "CHEF", "NUTRITION")

router = APIRouter(tags=["os-page"])

@router.get("/os")
def os_page(request: Request):
    denied = require_page_role(request, *OS_ROLES)
    if denied:
        return denied
    return FileResponse(TEMPLATE, media_type="text/html")
