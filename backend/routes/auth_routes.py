from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from backend.database.db import get_db
from backend.models.user import User
from backend.models.donor import Donor
from backend.models.receivers import Receiver
from backend.core.security import hash_password
from backend.core.security import verify_password, create_access_token


router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    name: str

    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    role: str

    phone: str
    country: str
    address: str

    latitude: float
    longitude: float
    pincode: int

    donor_type: str | None = None   

    #------------- REGISTER ------------------#

@router.post("/register", status_code=201)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):

    role = payload.role.lower().strip()

    if role not in ["donor", "receiver"]:
        raise HTTPException(
            status_code=400,
            detail="Role must be either 'donor' or 'receiver'"
        )

    # Check duplicate email
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create User
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create Profile
    if role == "donor":
        profile = Donor(
            name=payload.name,
            user_id=user.id,
            phone=payload.phone,
            country=payload.country,
            address=payload.address,
            latitude=payload.latitude,
            longitude=payload.longitude,
            pincode=payload.pincode,
            donor_type=payload.donor_type
        )

    else:  # receiver
        profile = Receiver(
            name= payload.name,
            user_id=user.id,
            phone=payload.phone,
            country=payload.country,
            address=payload.address,
            latitude=payload.latitude,
            longitude=payload.longitude,
            pincode=payload.pincode,
        )

    db.add(profile)
    db.commit()

    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "profile_id": profile.id
    }

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

#------------------- LOGIN ------------------#

@router.post("/login")
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        data={"user_id": user.id, "role": user.role}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
