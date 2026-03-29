from pydantic import BaseModel


class ReceiverOut(BaseModel):
    id: int
    user_id: int
    name: str
    phone: str
    country: str
    address: str
    latitude: float
    longitude: float
    pincode: int
    veg_only: str

    class Config:
        from_attributes = True

        