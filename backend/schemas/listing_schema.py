from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ListingCreate(BaseModel):
    food_name:   str
    quantity:    int
    food_type:   str
    # veg / non-veg / vegan / others / desserts / beverages / mains

    prepared_at: datetime
    expires_at:  datetime

    price: float


class ListingOut(BaseModel):
    id:          int
    donor_id:    int
    receiver_id: Optional[int] = None

    food_name:  str
    quantity:   int
    food_type:  str

    prepared_at: datetime
    expires_at:  datetime

    remaining_human_hours:   Optional[float] = None
    remaining_animal_hours:  Optional[float] = None
    remaining_compost_hours: Optional[float] = None

    redistribution_stage: str

    price:  float
    status: str

    created_at: datetime

    class Config:
        from_attributes = True