from app.models.volume import Volume
from sqlalchemy.orm import Session

def build_features(db:Session, target_time):
    row = (
        db.query(
            Volume.past_1_hour,
            Volume.past_1_day,
            Volume.past_1_week,
            Volume.past_1_month,
        )
        .filter(Volume.timestamp == target_time)
        .first()
    )

    return {
        "past_1_hour":  row.past_1_hour  if row else 0,
        "past_1_day":   row.past_1_day   if row else 0,
        "past_1_week":  row.past_1_week  if row else 0,
        "past_1_month": row.past_1_month if row else 0,
        "hour":         target_time.hour,
        "weekday":      target_time.weekday(),
    }