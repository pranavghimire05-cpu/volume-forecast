# app/ml/pipeline.py

import numpy as np
import pandas as pd
from datetime import timezone
from datetime import timedelta
import joblib
from datetime import timedelta
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import xgboost as xgb
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sqlalchemy.orm import Session

from app.models.volume import Volume

MODEL_PATH = Path("app/ml/volume_model.joblib")
FEATURES = ["past_1_hour", "past_1_day", "past_1_week", "past_1_month", "hour", "weekday"]
TARGET = "orders"
N_QUANTILE_MODELS = 2  # lower (0.1) and upper (0.9) bound models


# ─────────────────────────────────────────────
# 1. Load data from DB
# ─────────────────────────────────────────────

def load_training_data(db: Session) -> pd.DataFrame:
    from datetime import datetime
    now = (
    datetime.now(ZoneInfo("America/New_York"))
    .replace(minute=0, second=0, microsecond=0, tzinfo=None)
)

    rows = (
        db.query(Volume)
        .filter(Volume.timestamp <= now)   # real/historic rows, zeros included
        .order_by(Volume.timestamp)
        .all()
    )

    df = pd.DataFrame([{
        "timestamp":   r.timestamp,
        "orders":      r.orders,
        "past_1_hour":  r.past_1_hour,
        "past_1_day":   r.past_1_day,
        "past_1_week":  r.past_1_week,
        "past_1_month": r.past_1_month,
        "hour":         r.timestamp.hour,
        "weekday":      r.timestamp.weekday(),
    } for r in rows])

    return df


# ─────────────────────────────────────────────
# 2. Build pipelines (mean + quantile intervals)
# ─────────────────────────────────────────────

def build_pipeline(objective="reg:squarederror", quantile=None) -> Pipeline:
    params = dict(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
    )

    if quantile is not None:
        # Quantile regression for prediction intervals
        params.update(
            objective="reg:quantileerror",
            quantile_alpha=quantile,
        )
    else:
        params["objective"] = objective

    return Pipeline([
        ("scaler", StandardScaler()),
        ("model",  xgb.XGBRegressor(**params)),
    ])


# ─────────────────────────────────────────────
# 3. Train
# ─────────────────────────────────────────────

def train(db: Session) -> dict:
    df = load_training_data(db)

    X = df[FEATURES]
    y = df[TARGET]

    # TimeSeriesSplit — no data leakage
    tscv = TimeSeriesSplit(n_splits=5)

    # --- Mean prediction pipeline ---
    mean_pipeline = build_pipeline()

    mae_scores = []
    rmse_scores = []

    for train_idx, val_idx in tscv.split(X):
        mean_pipeline.fit(X.iloc[train_idx], y.iloc[train_idx])
        preds = mean_pipeline.predict(X.iloc[val_idx])
        mae_scores.append(mean_absolute_error(y.iloc[val_idx], preds))
        rmse_scores.append(np.sqrt(mean_squared_error(y.iloc[val_idx], preds)))

    # Final fit on all data
    mean_pipeline.fit(X, y)

    # --- Quantile pipelines for intervals ---
    lower_pipeline = build_pipeline(quantile=0.1)
    upper_pipeline = build_pipeline(quantile=0.9)

    lower_pipeline.fit(X, y)
    upper_pipeline.fit(X, y)

    # Save all three
    joblib.dump({
        "mean":  mean_pipeline,
        "lower": lower_pipeline,
        "upper": upper_pipeline,
    }, MODEL_PATH)

    return {
        "mae":  round(float(np.mean(mae_scores)), 2),
        "rmse": round(float(np.mean(rmse_scores)), 2),
        "rows": len(df),
    }


# ─────────────────────────────────────────────
# 4. Predict
# ─────────────────────────────────────────────

def load_models():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Model not trained yet. Call /train first.")
    return joblib.load(MODEL_PATH)

def predict_from_features(
        timestamp,
        past_1_hour,
        past_1_day,
        past_1_week,
        past_1_month,
    ) -> dict:
        models = load_models()

        if isinstance(timestamp, pd.Timestamp):
            timestamp = timestamp.to_pydatetime()

        timestamp = timestamp.replace(
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=None,
        )

        features = pd.DataFrame([{
            "past_1_hour": past_1_hour,
            "past_1_day": past_1_day,
            "past_1_week": past_1_week,
            "past_1_month": past_1_month,
            "hour": timestamp.hour,
            "weekday": timestamp.weekday(),
        }])

        predicted = max(
            0,
            round(float(models["mean"].predict(features)[0]))
        )

        lower_bound = max(
            0,
            round(float(models["lower"].predict(features)[0]))
        )

        upper_bound = max(
            0,
            round(float(models["upper"].predict(features)[0]))
        )

        return {
            "timestamp": timestamp.isoformat(),
            "predicted": predicted,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "interval": f"{lower_bound} – {upper_bound}",
        }


def predict(db: Session, target_time) -> dict:
    models = load_models()

    # Preserve the uploaded timestamp exactly as-is
    if isinstance(target_time, pd.Timestamp):
        target_time = target_time.to_pydatetime()

    target_time = target_time.replace(
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=None
    )

    row = (
        db.query(Volume)
        .filter(Volume.timestamp == target_time)
        .first()
    )

    if not row:
        raise ValueError(f"No row found for timestamp {target_time}")

    row = (
        db.query(Volume)
        .filter(Volume.timestamp >= target_time)
        .filter(Volume.timestamp < target_time + timedelta(hours=1))
        .first()
        )

    if not row:
        raise ValueError(f"No row found for timestamp {target_time}")
    
    features = pd.DataFrame([{
        "past_1_hour":  row.past_1_hour,
        "past_1_day":   row.past_1_day,
        "past_1_week":  row.past_1_week,
        "past_1_month": row.past_1_month,
        "hour":         target_time.hour,
        "weekday":      target_time.weekday(),
    }])

    predicted    = float(models["mean"].predict(features)[0])
    lower_bound  = float(models["lower"].predict(features)[0])
    upper_bound  = float(models["upper"].predict(features)[0])

    # Clamp negatives
    predicted   = max(0, round(predicted))
    lower_bound = max(0, round(lower_bound))
    upper_bound = max(0, round(upper_bound))

    return {
        "timestamp":   target_time.isoformat(),
        "predicted":   predicted,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "interval":    f"{lower_bound} – {upper_bound}",
    }


# ─────────────────────────────────────────────
# 5. Predict all future rows (orders == 0)
# ─────────────────────────────────────────────

def predict_future(
    db: Session,
    after_timestamp=None
) -> list[dict]:
    models = load_models()

    if after_timestamp is not None:
        cutoff = after_timestamp
        if isinstance(cutoff, pd.Timestamp):
            cutoff = cutoff.to_pydatetime()
        cutoff = cutoff.replace(minute=0, second=0, microsecond=0, tzinfo=None)
    else:
        cutoff = (
            datetime.now(ZoneInfo("America/New_York"))
            .replace(minute=0, second=0, microsecond=0, tzinfo=None)
        )

    future_rows = (
        db.query(Volume)
        .filter(Volume.timestamp > cutoff)
        .order_by(Volume.timestamp)
        .all()
    )

    if not future_rows:
        return []

    # Seed cache with historical real data so chained lookbacks work
    cache: dict = {}
    historical = (
        db.query(Volume.timestamp, Volume.orders)
        .filter(Volume.timestamp <= cutoff)
        .all()
    )
    for h in historical:
        cache[h.timestamp] = h.orders

    results = []

    for row in future_rows:
        ts = row.timestamp

        past_1_hour  = cache.get(ts - timedelta(hours=1),  0)
        past_1_day   = cache.get(ts - timedelta(days=1),   0)
        past_1_week  = cache.get(ts - timedelta(weeks=1),  0)
        past_1_month = cache.get(ts - timedelta(days=30),  0)

        features = pd.DataFrame([{
            "past_1_hour":  past_1_hour,
            "past_1_day":   past_1_day,
            "past_1_week":  past_1_week,
            "past_1_month": past_1_month,
            "hour":         ts.hour,
            "weekday":      ts.weekday(),
        }])

        predicted   = max(0, round(float(models["mean"].predict(features)[0])))
        lower_bound = max(0, round(float(models["lower"].predict(features)[0])))
        upper_bound = max(0, round(float(models["upper"].predict(features)[0])))

        cache[ts] = predicted

        row.orders       = predicted
        row.past_1_hour  = past_1_hour
        row.past_1_day   = past_1_day
        row.past_1_week  = past_1_week
        row.past_1_month = past_1_month

        results.append({
            "timestamp":   ts.isoformat(),
            "predicted":   predicted,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
        })

    db.commit()
    return results


