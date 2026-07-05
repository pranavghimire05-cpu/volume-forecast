from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.ml.pipeline import train

router = APIRouter(prefix="/train", tags=["train"])

@router.post("/")
def train_model(db: Session = Depends(get_db)):
    """Train on all historical data and save model."""
    metrics = train(db)
    return {"message": "Model trained", **metrics}