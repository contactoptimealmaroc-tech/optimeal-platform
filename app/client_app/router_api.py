from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..core.db import get_db
from ..core.models import User, ClientProfile, Subscription, Cycle, MenuDay
from ..core.security import require_roles
from .schemas import ON1In, ON2In, SubscriptionIn

router = APIRouter(prefix="/api/v1/client", tags=["client"])

def profile_for(db, user):
    p = db.scalar(select(ClientProfile).where(ClientProfile.user_id == user.id))
    if not p:
        raise HTTPException(404, "CLIENT_PROFILE_NOT_FOUND")
    return p

@router.get("/me")
def client_me(user: User = Depends(require_roles("CLIENT")), db: Session = Depends(get_db)):
    p = profile_for(db, user)
    return {"user_id": user.id, "profile_id": p.id, "full_name": p.full_name, "city": p.city, "sport": p.sport, "on1_completed": p.on1_completed, "on2_completed": p.on2_completed}

@router.post("/on1")
def on1(data: ON1In, user: User = Depends(require_roles("CLIENT")), db: Session = Depends(get_db)):
    p = profile_for(db, user); p.full_name = data.full_name; p.phone = data.phone; p.city = data.city; p.sport = data.sport; p.on1_completed = True; db.commit(); return {"status": "ON1_VALIDATED"}

@router.post("/on2")
def on2(data: ON2In, user: User = Depends(require_roles("CLIENT")), db: Session = Depends(get_db)):
    p = profile_for(db, user); p.address = data.address; p.allergies = data.allergies; p.intolerances = data.intolerances; p.preferences = data.preferences; p.on2_completed = True; db.commit(); return {"status": "ON2_VALIDATED"}

@router.post("/subscription")
def subscription(data: SubscriptionIn, user: User = Depends(require_roles("CLIENT")), db: Session = Depends(get_db)):
    p = profile_for(db, user); s = Subscription(client_id=p.id, plan_code=data.plan_code, status="ACTIVE"); db.add(s); db.commit(); return {"id": s.id, "plan_code": s.plan_code, "status": s.status}

@router.get("/menus")
def menus(user: User = Depends(require_roles("CLIENT")), db: Session = Depends(get_db)):
    p = profile_for(db, user); cycles = db.scalars(select(Cycle).where(Cycle.client_id == p.id).order_by(Cycle.start_date.desc())).all(); out = []
    for c in cycles:
        rows = db.scalars(select(MenuDay).where(MenuDay.cycle_id == c.id).order_by(MenuDay.service_date)).all(); out.append({"cycle_id": c.id, "start_date": c.start_date, "end_date": c.end_date, "status": c.status, "days": [{"date": x.service_date, "recipe_id": x.recipe_id, "status": x.status} for x in rows]})
    return out
