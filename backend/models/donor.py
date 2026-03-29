from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from backend.database.db import Base
from fastapi import Depends, HTTPException, status
from backend.core.dependencies import get_current_user, require_role
from fastapi import APIRouter

router = APIRouter()


class Donor(Base):
    __tablename__ = "donors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    name = Column(String)
    address = Column(String, nullable=False)

    phone = Column(String, nullable=False)
    country = Column(String, nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    pincode = Column(Integer, nullable=False)

    donor_type = Column(String)  
    # bakery / restaurant / caterer

    user = relationship("User")

#------------------- Role based access control ------------------

@router.post("/create-food")
def create_food_listing(
    current_user=Depends(require_role("donor"))
):
    return {"message": "Food listing created"}

