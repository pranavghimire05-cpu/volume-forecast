import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.db.database import SessionLocal 
from app.ml.pipeline import train


def main():
    db = SessionLocal()
    try:
        print("Starting training run...")
        metrics = train(db)
        print("Training complete.")
        print(f"Rows used:        {metrics['rows']}")
        print(f"MAE (avg fold):   {metrics['mae']}")
        print(f"RMSE (avg fold):  {metrics['rmse']}")
    except Exception as e:
        print(f"Training failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()