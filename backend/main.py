from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.db import engine, Base

# Import models so SQLAlchemy sees them
from backend.models.user import User
from backend.models.receivers import Receiver
from backend.models.donor import Donor
from backend.models.listing import FoodListing

app = FastAPI(title="Second Serve API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if True else ["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables---------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "Backend running"}

from backend.routes import auth_routes, donor_routes, receivers_routes, listing_routes

app.include_router(auth_routes.router)
app.include_router(donor_routes.router)
app.include_router(receivers_routes.router)
app.include_router(listing_routes.router)