from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.models.listing import FoodListing
from backend.models.donor import Donor
from backend.schemas.listing_schema import ListingCreate, ListingOut
from backend.core.dependencies import require_role
from backend.services.ml_service import predict_food_timeline
from backend.services.matching_service import find_nearest_receivers
from backend.services.notification_service import notify_receiver


router = APIRouter(prefix="/listings", tags=["Listings"])


#------------------- CREATE LISTING ------------------#

@router.post("/", status_code=201, response_model=ListingOut)
def create_listing(
    payload: ListingCreate,
    current_user=Depends(require_role("donor")),
    db: Session = Depends(get_db)
):
    donor = db.query(Donor).filter(Donor.user_id == current_user["user_id"]).first()

    if not donor:
        raise HTTPException(status_code=404, detail="Donor profile not found")

    # Run ML timeline prediction
    timeline = predict_food_timeline(
        food_name=payload.food_name,
        food_type=payload.food_type,
        prepared_at=payload.prepared_at
    )

    listing = FoodListing(
        donor_id=donor.id,
        food_name=payload.food_name,
        quantity=payload.quantity,
        food_type=payload.food_type,
        prepared_at=payload.prepared_at,
        expires_at=payload.expires_at,
        remaining_human_hours=timeline['remaining_human_hours'],
        remaining_animal_hours=timeline['remaining_animal_hours'],
        remaining_compost_hours=timeline['remaining_compost_hours'],
        redistribution_stage=timeline['redistribution_stage'],
        price=payload.price
    )

    db.add(listing)
    db.commit()
    db.refresh(listing)

    # Notify nearest receivers
    nearest = find_nearest_receivers(
        donor_lat=donor.latitude,
        donor_lon=donor.longitude,
        db=db,
        food_type=payload.food_type,
        limit=5
    )

    for rec in nearest:
        notify_receiver(
            receiver_name=rec['name'],
            food_name=payload.food_name,
            donor_address=donor.address
        )

    return listing


#------------------- GET ALL AVAILABLE LISTINGS ------------------#

@router.get("/available", response_model=list[ListingOut])
def get_available_listings(db: Session = Depends(get_db)):

    listings = (
        db.query(FoodListing)
        .filter(FoodListing.status == "available")
        .all()
    )

    return listings


#------------------- GET NEAREST RECEIVERS FOR A LISTING ------------------#

@router.get("/{listing_id}/nearest-receivers")
def get_nearest_receivers(
    listing_id: int,
    current_user=Depends(require_role("donor")),
    db: Session = Depends(get_db)
):
    listing = db.query(FoodListing).filter(FoodListing.id == listing_id).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    donor = db.query(Donor).filter(Donor.id == listing.donor_id).first()

    nearest = find_nearest_receivers(
        donor_lat=donor.latitude,
        donor_lon=donor.longitude,
        db=db,
        food_type=listing.food_type,
        limit=5
    )

    return {
        "listing_id":       listing_id,
        "nearest_receivers": nearest
    }