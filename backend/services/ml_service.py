import numpy as np
import pandas as pd
import joblib
import os
from datetime import datetime, timezone


# ----------------------------------------------------------------
# PATHS
# ----------------------------------------------------------------

ML_DIR = os.path.join(
    os.path.dirname(__file__), '..', '..', 'ml_pipeline', 'models'
)


# ----------------------------------------------------------------
# LOAD MODELS AND ENCODERS
# Falls back to rule-based if notebooks have not been run yet
# ----------------------------------------------------------------

_models_loaded = False

try:
    model_human   = joblib.load(os.path.join(ML_DIR, 'model_human.pkl'))
    model_animal  = joblib.load(os.path.join(ML_DIR, 'model_animal.pkl'))
    model_compost = joblib.load(os.path.join(ML_DIR, 'model_compost.pkl'))
    model_stage   = joblib.load(os.path.join(ML_DIR, 'model_stage.pkl'))
    le_food_type  = joblib.load(os.path.join(ML_DIR, 'le_food_type.pkl'))
    le_category   = joblib.load(os.path.join(ML_DIR, 'le_category.pkl'))
    le_storage    = joblib.load(os.path.join(ML_DIR, 'le_storage.pkl'))
    le_risk       = joblib.load(os.path.join(ML_DIR, 'le_risk.pkl'))
    le_stage      = joblib.load(os.path.join(ML_DIR, 'le_stage.pkl'))
    food_ref      = pd.read_csv(os.path.join(ML_DIR, 'food_reference.csv'))
    _models_loaded = True
    print("[ml_service] ML models loaded successfully")

except Exception as e:
    print(f"[ml_service] Models not found — using rule-based fallback. Reason: {e}")


# ----------------------------------------------------------------
# RULE-BASED FALLBACK
# Used before notebooks are run
# ----------------------------------------------------------------

FALLBACK = {
    'veg':       {'human': 6,  'animal': 12, 'compost': 24},
    'non-veg':   {'human': 4,  'animal': 8,  'compost': 18},
    'vegan':     {'human': 5,  'animal': 10, 'compost': 20},
    'desserts':  {'human': 8,  'animal': 16, 'compost': 30},
    'beverages': {'human': 4,  'animal': 8,  'compost': 18},
    'mains':     {'human': 5,  'animal': 10, 'compost': 22},
    'snacks':    {'human': 6,  'animal': 12, 'compost': 24},
    'others':    {'human': 5,  'animal': 10, 'compost': 20},
}


def _rule_based(food_type: str, hours_since_prep: float):
    h = FALLBACK.get(food_type.lower(), FALLBACK['veg'])

    remaining_human   = round(max(0, h['human']   - hours_since_prep), 2)
    remaining_animal  = round(max(0, h['animal']  - hours_since_prep), 2)
    remaining_compost = round(max(0, h['compost'] - hours_since_prep), 2)

    if hours_since_prep <= h['human']:
        stage = 'human'
    elif hours_since_prep <= h['animal']:
        stage = 'animal'
    elif hours_since_prep <= h['compost']:
        stage = 'compost'
    else:
        stage = 'waste'

    return remaining_human, remaining_animal, remaining_compost, stage


# ----------------------------------------------------------------
# MAIN PREDICTION FUNCTION
# Called by listing_routes.py on every new listing
# ----------------------------------------------------------------

def predict_food_timeline(food_name: str, food_type: str, prepared_at: datetime):
    """
    Returns remaining hours for each stage and current redistribution stage.
    Uses trained ML models if available, otherwise rule-based fallback.
    """

    now = datetime.now(timezone.utc)

    if prepared_at.tzinfo is None:
        prepared_at = prepared_at.replace(tzinfo=timezone.utc)

    hours_since_prep = round(max(0, (now - prepared_at).total_seconds() / 3600), 2)

    # ---- ML path ----
    if _models_loaded:
        match = food_ref[food_ref['food_name'].str.lower() == food_name.lower()]

        if match.empty:
            match = food_ref[food_ref['food_type'] == food_type.lower()]

        if match.empty:
            match = food_ref.iloc[[0]]

        row = match.iloc[0]

        try:
            features = np.array([[
                le_food_type.transform([row['food_type']])[0],
                le_category.transform([row['category']])[0],
                le_storage.transform([row['storage_temp']])[0],
                le_risk.transform([row['risk_level']])[0],
                float(row['human_safe_hours']),
                float(row['animal_safe_hours']),
                float(row['compost_hours']),
                hours_since_prep
            ]])

            remaining_human   = round(max(0, model_human.predict(features)[0]), 2)
            remaining_animal  = round(max(0, model_animal.predict(features)[0]), 2)
            remaining_compost = round(max(0, model_compost.predict(features)[0]), 2)

            stage_enc = model_stage.predict(features)[0]
            stage     = le_stage.inverse_transform([stage_enc])[0]

            return {
                'hours_since_prep':        hours_since_prep,
                'remaining_human_hours':   remaining_human,
                'remaining_animal_hours':  remaining_animal,
                'remaining_compost_hours': remaining_compost,
                'redistribution_stage':    stage
            }

        except Exception as e:
            print(f"[ml_service] Prediction error — falling back. {e}")

    # ---- Fallback path ----
    rh, ra, rc, stage = _rule_based(food_type, hours_since_prep)

    return {
        'hours_since_prep':        hours_since_prep,
        'remaining_human_hours':   rh,
        'remaining_animal_hours':  ra,
        'remaining_compost_hours': rc,
        'redistribution_stage':    stage
    }