from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
from backend.database.db import Base


class FoodListing(Base):
    __tablename__ = "food_listings"

    id = Column(Integer, primary_key=True, index=True)

    donor_id    = Column(Integer, ForeignKey("donors.id"))
    receiver_id = Column(Integer, ForeignKey("receivers.id"), nullable=True)

    food_name = Column(String, nullable=False)
    quantity  = Column(Integer, nullable=False)

    food_type = Column(String)
    # veg / non-veg / vegan / others / desserts / beverages / mains

    prepared_at = Column(DateTime(timezone=True), nullable=False)
    expires_at  = Column(DateTime(timezone=True), nullable=False)

    # ML predicted timelines — filled on listing creation
    remaining_human_hours   = Column(Float, nullable=True)
    remaining_animal_hours  = Column(Float, nullable=True)
    remaining_compost_hours = Column(Float, nullable=True)

    redistribution_stage = Column(String, default="human")
    # human / animal / compost / waste

    price = Column(Float, nullable=False)

    status = Column(String, default="available")
    # available / reserved / collected / expired

    created_at = Column(DateTime(timezone=True), server_default=func.now())

