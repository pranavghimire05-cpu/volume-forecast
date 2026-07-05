import pandas as pd
import numpy as np
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.config import team_captains
from app.models.performance import Performance


def normalize_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df

async def process_performance_file(
    file: UploadFile,
    db: Session
):
    df = pd.read_csv(file.file)
    

    # Transform data
    df = normalize_columns(df)
    df = df[~df["name"].isin(team_captains)]
    df["mph"] = df["analyzed"] / df["analysis_hours"]
    df["rph"] = df["reviewed"] / df["review_hours"]

    df["role"] = np.select(
    [
        df["name"].isin(team_captains),
        df["reviewed"].notna()
    ],
    [
        "team_captain",
        "reviewer"
    ],
    default="analyst"
)
    df["accuracy"] = pd.to_numeric(
    df["passing"].astype(str).str.replace("%", ""),
    errors="coerce"
)
    max_mph = df["mph"].fillna(0).max()

    if max_mph > 0:
        df["mph_score"] = (
        df["mph"].fillna(0) / max_mph
    ) * 100
    else:
        df["mph_score"] = 0

    reviewer_mask = df["role"].str.lower() == "reviewer"

    max_rph = df.loc[reviewer_mask, "rph"].fillna(0).max()

    if max_rph > 0:
        df.loc[reviewer_mask, "rph_score"] = (
        df.loc[reviewer_mask, "rph"].fillna(0) / max_rph
        ) * 100
    else:
        df.loc[reviewer_mask, "rph_score"] = 0
    
    # Analysts
    df.loc[df["role"] == "analyst", "rating"] = (
    df["accuracy"] * 0.7 +
    df["mph_score"] * 0.3
    )

    # Reviewers
    df.loc[df["role"] == "reviewer", "rating"] = (
    df["accuracy"] * 0.7 +
    df["rph_score"] * 0.3
    )

    df["rating"] = df["rating"].round(2)
    
    
    # Convert DataFrame to list of dictionaries
    df = df.replace([np.inf, -np.inf], np.nan)
    
    records = df.to_dict(orient="records")

    db.bulk_insert_mappings(
        Performance,
        records
    )

    db.commit()

    return {
        "message": "Upload successful",
        "rows_processed": len(records)
    }