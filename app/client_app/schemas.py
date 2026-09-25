from pydantic import BaseModel, Field

class ON1In(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    phone: str = Field(default="", max_length=40)
    city: str = Field(default="Rabat", max_length=80)
    sport: bool = False

class ON2In(BaseModel):
    address: str = Field(min_length=5, max_length=300)
    allergies: str = ""
    intolerances: str = ""
    preferences: str = ""

class SubscriptionIn(BaseModel):
    plan_code: str = Field(min_length=2, max_length=40)
