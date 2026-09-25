from datetime import timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..core.models import ClientProfile, Cycle, MenuDay, Recipe

def build_cycle_menu(db: Session, cycle: Cycle, client: ClientProfile):
    """Frontière du moteur de menu côté serveur. Les règles métier vivent ici, jamais dans du JS public."""
    days = []
    d = cycle.start_date
    while d <= cycle.end_date:
        days.append(d); d += timedelta(days=1)
    existing = {x.service_date: x for x in db.scalars(select(MenuDay).where(MenuDay.cycle_id == cycle.id)).all()}
    recipes = db.scalars(select(Recipe).where(Recipe.active.is_(True)).order_by(Recipe.id)).all()
    # Moteur déterministe initial : sélectionne des recettes en respectant les allergènes.
    blocked = {x.strip().lower() for x in (client.allergies + "," + client.intolerances).split(",") if x.strip()}
    usable = [r for r in recipes if not blocked.intersection({a.strip().lower() for a in r.allergens.split(",") if a.strip()})]
    for idx, day in enumerate(days):
        if day in existing:
            continue
        recipe = usable[idx % len(usable)] if usable else None
        db.add(MenuDay(cycle_id=cycle.id, service_date=day, recipe_id=recipe.id if recipe else None, status="PROPOSED"))
    db.commit()
