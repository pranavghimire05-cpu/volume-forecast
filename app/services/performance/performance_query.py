from sqlalchemy.orm import Session
from app.models.performance import Performance

def get_all_performance_rows(db: Session, limit: int = 1000):
    rows = db.query(Performance).limit(limit).all()

    return [
        {
            "id": r.id,
            "name": r.name,
            "role": r.role,
            "mph": r.mph,
            "rph": r.rph,
            "accuracy": r.accuracy,
            "rating": r.rating,
        }
        for r in rows
    ]