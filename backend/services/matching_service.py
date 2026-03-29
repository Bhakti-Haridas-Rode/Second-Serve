import numpy as np
import pandas as pd
import joblib
import math
import os
from sqlalchemy.orm import Session
from backend.models.receivers import Receiver


# ----------------------------------------------------------------
# PATHS
# ----------------------------------------------------------------

ML_DIR = os.path.join(
    os.path.dirname(__file__), '..', '..', 'ml_pipeline', 'models'
)


# ----------------------------------------------------------------
# LOAD KNN BALLTREE
# Falls back to haversine on live DB if not found
# ----------------------------------------------------------------

_knn_loaded = False

try:
    knn_tree = joblib.load(os.path.join(ML_DIR, 'knn_receiver_tree.pkl'))
    knn_ref  = pd.read_csv(os.path.join(ML_DIR, 'receivers_reference.csv'))
    _knn_loaded = True
    print("[matching_service] KNN model loaded successfully")

except Exception as e:
    print(f"[matching_service] KNN not loaded — using haversine fallback. Reason: {e}")


# ----------------------------------------------------------------
# HAVERSINE FORMULA
# ----------------------------------------------------------------

def _haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(d_lon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ----------------------------------------------------------------
# MAIN MATCHING FUNCTION
# Called by listing_routes.py after a listing is created
# ----------------------------------------------------------------

def find_nearest_receivers(
    donor_lat:  float,
    donor_lon:  float,
    db:         Session,
    food_type:  str = None,
    limit:      int = 5
):
    """
    Finds nearest receivers to a donor location.
    Filters veg_only receivers if food is non-veg.
    Returns list sorted by distance ascending.
    """

    receivers = db.query(Receiver).all()

    if not receivers:
        return []

    # Filter veg_only for non-veg food
    if food_type and food_type.lower() == 'non-veg':
        receivers = [r for r in receivers if r.veg_only == 'no']

    if not receivers:
        return []

    results = []

    # ---- KNN path ----
    if _knn_loaded and len(receivers) > 0:
        try:
            donor_rad   = np.radians([[donor_lat, donor_lon]])
            k           = min(limit, len(receivers))
            distances, indices = knn_tree.query(donor_rad, k=k)
            distances_km = distances[0] * 6371

            for dist_km, idx in zip(distances_km, indices[0]):
                ref_row = knn_ref.iloc[idx]
                for r in receivers:
                    if (abs(r.latitude  - ref_row['latitude'])  < 0.01 and
                        abs(r.longitude - ref_row['longitude']) < 0.01):
                        results.append({
                            'receiver_id': r.id,
                            'name':        r.name,
                            'address':     r.address,
                            'distance_km': round(dist_km, 2),
                            'veg_only':    r.veg_only
                        })
                        break

        except Exception as e:
            print(f"[matching_service] KNN query failed — using haversine. {e}")
            results = []

    # ---- Haversine fallback ----
    if not results:
        for r in receivers:
            dist_km = _haversine_km(donor_lat, donor_lon, r.latitude, r.longitude)
            results.append({
                'receiver_id': r.id,
                'name':        r.name,
                'address':     r.address,
                'distance_km': round(dist_km, 2),
                'veg_only':    r.veg_only
            })

    results.sort(key=lambda x: x['distance_km'])

    return results[:limit]