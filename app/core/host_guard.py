"""
DOMAIN_ARCHITECTURE.md décrit 3 domaines distincts :
  optimeal.ma      -> vitrine publique uniquement
  app.optimeal.ma  -> espace applicatif (connexion / client / os) uniquement
  api.optimeal.ma  -> API JSON uniquement

Avant V27, nginx pointait déjà ces 3 domaines vers le même process FastAPI,
mais rien dans le code n'empêchait, par exemple, app.optimeal.ma de servir
aussi la vitrine, ou optimeal.ma de répondre sur /api/*. La séparation
n'existait que dans la documentation.

Ce middleware la fait respecter réellement, en se basant sur les 3 URLs déjà
présentes dans la config (PUBLIC_BASE_URL / APP_BASE_URL / API_BASE_URL).

En local (les 3 valeurs par défaut pointent vers 127.0.0.1:8000), les 3 "hôtes"
sont identiques : le middleware se met alors en veille et ne change rien au
comportement de développement.
"""
from urllib.parse import urlparse
from fastapi import Request
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .config import settings

def _hostname(url: str) -> str:
    return (urlparse(url).hostname or "").lower()

APP_ONLY_PREFIXES = ("/connexion", "/client", "/os")

class DomainBoundaryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_host = _hostname(settings.public_base_url)
        app_host = _hostname(settings.app_base_url)
        api_host = _hostname(settings.api_base_url)

        if len({public_host, app_host, api_host}) <= 1:
            return await call_next(request)  # mono-hôte (dev local) : rien à imposer

        host = (request.url.hostname or "").lower()
        path = request.url.path
        is_app_only = path.startswith(APP_ONLY_PREFIXES)
        is_api = path.startswith("/api/")

        if host == public_host and (is_app_only or is_api):
            if is_api:
                return JSONResponse({"detail": "NOT_FOUND"}, status_code=404)
            return RedirectResponse(f"{settings.app_base_url}{path}")

        if host == app_host:
            if path == "/":
                return RedirectResponse("/connexion")
            if not (is_app_only or is_api or path == "/api/v1/health"):
                return RedirectResponse(f"{settings.public_base_url}{path}")

        if host == api_host and not (is_api or path == "/api/v1/health"):
            return JSONResponse({"detail": "NOT_FOUND"}, status_code=404)

        return await call_next(request)
