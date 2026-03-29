from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from backend.database.db import Base

class Receiver(Base):
    __tablename__ = "receivers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    
    phone = Column(String, nullable=False)
    country = Column(String, nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    pincode = Column(Integer, nullable=False)

    veg_only = Column(String, default="no")  
    # yes / no

    user = relationship("User")