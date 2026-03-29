from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.models.receivers import Receiver
from backend.core.dependencies import get_current_user, require_role


router = APIRouter(prefix="/receiver", tags=["Receiver"])


#------------------- GET RECEIVER PROFILE ------------------#

@router.get("/profile")
def get_receiver_profile(
    current_user=Depends(require_role("receiver")),
    db: Session = Depends(get_db)
):
    receiver = db.query(Receiver).filter(Receiver.user_id == current_user["user_id"]).first()

    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver profile not found")

    return receiver