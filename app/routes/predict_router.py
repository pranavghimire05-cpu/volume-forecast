from fastapi import APIRouter, Depends
from datetime import datetime
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.ml.pipeline import predict, predict_future
router = APIRouter(prefix="/predict", tags=["predict"])

@router.get("/")
def predict_single(timestamp: datetime, db: Session = Depends(get_db)):
    """Predict orders for a single timestamp."""
    return predict(db, timestamp)


@router.get("/future")
def predict_all_future(db: Session = Depends(get_db)):
    """Predict and store orders for all future rows."""
    return predict_future(db)