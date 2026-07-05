import pandas as pd
import io
from app.services.volume.volume_service import process_volume_file
from app.services.performance.performance_service import process_performance_file
from fastapi import APIRouter, UploadFile, File, Depends
from app.db.database import get_db
from sqlalchemy.orm import Session



router = APIRouter(prefix="/volume", tags=["volume"])


@router.post("/")
async def upload_volume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Parse timestamp
    # Clean column values
    df["date"] = df["date"].astype(str).str.strip()
    df["hour"] = df["hour"].astype(str).str.strip()

    # Combine date and hour
    combined = df["date"] + " " + df["hour"]

    # Parse timestamps (supports both with and without seconds)
    df["timestamp"] = pd.to_datetime(
        combined,
        errors="coerce"
    )

    # Check for invalid timestamps
    if df["timestamp"].isna().any():
        bad_rows = df.loc[df["timestamp"].isna(), ["date", "hour"]]
        raise ValueError(
            f"Invalid date/hour values:\n{bad_rows.to_string(index=False)}"
        )

    # Keep only what we need
    df = df[["timestamp", "orders"]].copy()
    df["orders"] = pd.to_numeric(df["orders"], errors="coerce").fillna(0).astype(int)

    # =========================================================
    # Fill ALL missing hours with orders=0
    # so DB always has a complete hourly sequence
    # =========================================================
    full_range = pd.date_range(
        start=df["timestamp"].min(),
        end=df["timestamp"].max(),
        freq="h"
    )
    df = df.set_index("timestamp").reindex(full_range, fill_value=0).reset_index()
    df.columns = ["timestamp", "orders"]

    print(f"DEBUG: CSV rows={len(df)}, range={df['timestamp'].min()} → {df['timestamp'].max()}")

    # Convert to records with pre-parsed timestamp
    records = df.to_dict(orient="records")

    return await process_volume_file(db=db, records=records)