from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.models.donor import Donor
from backend.core.dependencies import get_current_user, require_role


router = APIRouter(prefix="/donor", tags=["Donor"])


#------------------- GET DONOR PROFILE ------------------#

@router.get("/profile")
def get_donor_profile(
    current_user=Depends(require_role("donor")),
    db: Session = Depends(get_db)
):
    donor = db.query(Donor).filter(Donor.user_id == current_user["user_id"]).first()

    if not donor:
        raise HTTPException(status_code=404, detail="Donor profile not found")

    return donor