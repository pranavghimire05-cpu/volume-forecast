import pandas as pd
from datetime import timedelta
from sqlalchemy import func
from app.models.volume import Volume
from .features import build_features
from sqlalchemy.orm import Session

def build_dataset(db:Session, timestamps: list):
    rows = []

    for t in timestamps:
        features = build_features(db, t)

        label = (
            db.query(func.sum(Volume.orders))
            .filter(
                Volume.timestamp >= t,
                Volume.timestamp < t + timedelta(minutes=1)
            )
            .scalar()
            or 0
        )

        rows.append({**features, "label": label})

    return pd.DataFrame(rows)