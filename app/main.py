from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.db import Base, engine
from .core.host_guard import DomainBoundaryMiddleware

from .site.router import router as site_router
from .auth.router_api import router as auth_api_router
from .auth.router_page import router as auth_page_router
from .client_app.router_api import router as client_api_router
from .client_app.router_page import router as client_page_router
from .admin_app.router_api import router as admin_api_router
from .admin_app.router_page import router as admin_page_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OptiMeal API",
    version="27.0.0",
    docs_url="/api/docs" if settings.app_env != "production" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
)
# Impose en code la frontière vitrine / app / api documentée dans DOMAIN_ARCHITECTURE.md
app.add_middleware(DomainBoundaryMiddleware)

# main.py n'est qu'un chef d'orchestre : chaque module reste responsable
# de son propre domaine (vitrine publique / auth / client / admin).
app.include_router(site_router)
app.include_router(auth_api_router)
app.include_router(auth_page_router)
app.include_router(client_api_router)
app.include_router(client_page_router)
app.include_router(admin_api_router)
app.include_router(admin_page_router)

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "service": "optimeal-backend", "version": "27.0.0"}
