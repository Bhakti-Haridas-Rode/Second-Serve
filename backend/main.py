from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from backend.database.db import engine, Base
from backend.core.dependencies import get_current_user

# Import models so SQLAlchemy sees them
from backend.models.user import User
from backend.models.receivers import Receiver
from backend.models.donor import Donor
from backend.models.listing import FoodListing

from backend.routes import auth_routes, donor_routes, receivers_routes, listing_routes

app = FastAPI(title="Second Serve API")

# ── CORS — allows any browser anywhere in the world to call this API ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all database tables on startup
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "Second Serve API is running"}


# Register all routers
app.include_router(auth_routes.router)
app.include_router(donor_routes.router)
app.include_router(receivers_routes.router)
app.include_router(listing_routes.router)


#----------- protected test route -----------#
@app.get("/protected")
def protected_route(current_user=Depends(get_current_user)):
    return {"message": "You are authenticated", "user": current_user}