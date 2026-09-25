from datetime import date
from pydantic import BaseModel, ConfigDict

class CycleIn(BaseModel):
    client_id: int
    start_date: date
    end_date: date

class MenuGenerateIn(BaseModel):
    cycle_id: int

class RecipeIn(BaseModel):
    name: str
    pole: str
    calories: int | None = None
    protein_g: int | None = None
    carbs_g: int | None = None
    fat_g: int | None = None
    allergens: str = ""

class RecipeOut(RecipeIn):
    id: int
    model_config = ConfigDict(from_attributes=True)
