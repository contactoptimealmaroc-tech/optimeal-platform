from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..core.db import get_db
from ..core.models import User, ClientProfile, Cycle, Recipe, MenuDay
from ..core.security import require_roles
from .schemas import CycleIn, MenuGenerateIn, RecipeIn
from .services import build_cycle_menu

router = APIRouter(prefix="/api/v1/os", tags=["os"])
OS_ROLES = ("ADMIN", "CHEF", "NUTRITION")

@router.get("/dashboard")
def dashboard(user: User = Depends(require_roles(*OS_ROLES)), db: Session = Depends(get_db)):
    return {"role": user.role, "clients": db.query(ClientProfile).count(), "cycles": db.query(Cycle).count(), "recipes": db.query(Recipe).count()}

@router.get("/clients")
def clients(user: User = Depends(require_roles(*OS_ROLES)), db: Session = Depends(get_db)):
    rows = db.scalars(select(ClientProfile).order_by(ClientProfile.id.desc())).all(); return [{"id": p.id, "full_name": p.full_name, "city": p.city, "on1": p.on1_completed, "on2": p.on2_completed} for p in rows]

@router.post("/cycles")
def create_cycle(data: CycleIn, user: User = Depends(require_roles(*OS_ROLES)), db: Session = Depends(get_db)):
    client = db.get(ClientProfile, data.client_id)
    if not client:
        raise HTTPException(404, "CLIENT_NOT_FOUND")
    if data.end_date < data.start_date:
        raise HTTPException(422, "INVALID_DATES")
    c = Cycle(client_id=data.client_id, start_date=data.start_date, end_date=data.end_date, status="DRAFT"); db.add(c); db.commit(); db.refresh(c); return {"id": c.id, "status": c.status}

@router.post("/menus/generate")
def generate_menu(data: MenuGenerateIn, user: User = Depends(require_roles(*OS_ROLES)), db: Session = Depends(get_db)):
    c = db.get(Cycle, data.cycle_id)
    if not c:
        raise HTTPException(404, "CYCLE_NOT_FOUND")
    client = db.get(ClientProfile, c.client_id)
    build_cycle_menu(db, c, client); c.status = "GENERATED"; db.commit(); return {"cycle_id": c.id, "status": c.status}

@router.post("/recipes")
def create_recipe(data: RecipeIn, user: User = Depends(require_roles("ADMIN", "CHEF", "NUTRITION")), db: Session = Depends(get_db)):
    r = Recipe(**data.model_dump()); db.add(r); db.commit(); db.refresh(r); return {"id": r.id, "name": r.name, "pole": r.pole}

@router.get("/recipes")
def recipes(user: User = Depends(require_roles(*OS_ROLES)), db: Session = Depends(get_db)):
    return [{"id": r.id, "name": r.name, "pole": r.pole, "calories": r.calories, "protein_g": r.protein_g, "carbs_g": r.carbs_g, "fat_g": r.fat_g, "allergens": r.allergens} for r in db.scalars(select(Recipe).where(Recipe.active.is_(True)).order_by(Recipe.id)).all()]
