from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.orm import Session

from app.models.volume import Volume
from app.ml.pipeline import MODEL_PATH, predict_future


async def process_volume_file(
    db: Session,
    records: list[dict]
):
    # =========================================================
    # DEBUG
    # =========================================================
    print(f"DEBUG: received {len(records)} records")
    if records:
        print(f"DEBUG: first record = {records[0]}")

    latest_timestamp = None

    # =========================================================
    # Parse timestamp — defined once, used throughout
    # =========================================================
    def parse_ts(record):
        ts = record.get("timestamp")
        if isinstance(ts, datetime):
            return ts
        if isinstance(ts, pd.Timestamp):
            return ts.to_pydatetime()
        # Fallback for raw date/hour strings
        return datetime.strptime(
            f"{record['date']} {record['hour']}",
            "%m/%d/%Y %I:%M:%S %p"
        )

    # =========================================================
    # DB lookup helper — defined once, used throughout
    # =========================================================
    def get_orders_at(target_ts):
        val = (
            db.query(Volume.orders)
            .filter(Volume.timestamp == target_ts)
            .scalar()
        )
        return int(val) if val is not None else 0

    # =========================================================
    # Sort records by timestamp before processing
    # =========================================================
    try:
        records = sorted(records, key=parse_ts)
    except Exception as e:
        print(f"ERROR sorting records: {e}")
        raise

    # =========================================================
    # Process and upsert each real (historical/actual) record.
    # NOTE: `orders` here always comes from the uploaded file —
    # the model is NEVER used to fill in historical rows.
    # =========================================================
    for record in records:
        try:
            timestamp = parse_ts(record)
        except Exception as e:
            print(f"ERROR parsing timestamp for record {record}: {e}")
            continue

        orders = record.get("orders")
        if orders is None or (isinstance(orders, float) and pd.isna(orders)):
            orders = 0
        else:
            orders = int(orders)

        if latest_timestamp is None or timestamp > latest_timestamp:
            latest_timestamp = timestamp

        past_1_hour  = get_orders_at(timestamp - timedelta(hours=1))
        past_1_day   = get_orders_at(timestamp - timedelta(days=1))
        past_1_week  = get_orders_at(timestamp - timedelta(weeks=1))
        past_1_month = get_orders_at(timestamp - timedelta(days=30))

        try:
            existing = (
                db.query(Volume)
                .filter(Volume.timestamp == timestamp)
                .first()
            )

            if existing:
                existing.orders       = orders
                existing.past_1_hour  = past_1_hour
                existing.past_1_day   = past_1_day
                existing.past_1_week  = past_1_week
                existing.past_1_month = past_1_month
            else:
                db.add(Volume(
                    timestamp=timestamp,
                    orders=orders,
                    past_1_hour=past_1_hour,
                    past_1_day=past_1_day,
                    past_1_week=past_1_week,
                    past_1_month=past_1_month,
                ))

            db.flush()

        except Exception as e:
            print(f"ERROR inserting/updating row at {timestamp}: {e}")
            db.rollback()
            raise

    # =========================================================
    # Future placeholder rows — created only after all real rows
    # are flushed. These start at orders=0 and lookback values
    # computed relative to themselves; actual predictions are
    # filled in afterwards by predict_future(), which is scoped
    # strictly to timestamp > latest_timestamp (the real cutoff),
    # never to historical rows.
    # =========================================================
    if latest_timestamp:
        deleted = (
            db.query(Volume)
            .filter(Volume.timestamp > latest_timestamp)
            .delete(synchronize_session=False)
        )

        print(f"Deleted {deleted} old prediction rows.")

        db.flush()

        start_timestamp = latest_timestamp + timedelta(hours=1)

        print(f"Generating future placeholder rows from {start_timestamp}")

        prediction_cache = {}

        historical = (
            db.query(Volume.timestamp, Volume.orders)
            .filter(Volume.timestamp <= latest_timestamp)
            .all()
        )

        for row in historical:
            prediction_cache[row.timestamp] = row.orders

        for i in range(168):
            future_timestamp = start_timestamp + timedelta(hours=i)

            past_1_hour = prediction_cache.get(
                future_timestamp - timedelta(hours=1), 0
            )

            past_1_day = prediction_cache.get(
                future_timestamp - timedelta(days=1), 0
            )

            past_1_week = prediction_cache.get(
                future_timestamp - timedelta(weeks=1), 0
            )

            past_1_month = prediction_cache.get(
                future_timestamp - timedelta(days=30), 0
            )

            # Placeholder only — real value (if a model exists) is
            # filled in by predict_future() below.
            prediction_cache[future_timestamp] = 0

            db.add(
                Volume(
                    timestamp=future_timestamp,
                    orders=0,
                    past_1_hour=past_1_hour,
                    past_1_day=past_1_day,
                    past_1_week=past_1_week,
                    past_1_month=past_1_month,
                )
            )

        db.flush()

    # =========================================================
    # Final commit of real rows + future placeholders
    # =========================================================
    try:
        db.commit()
        total = db.query(Volume).count()
        print(f"DEBUG: committed — total rows in DB: {total}")
    except Exception as e:
        print(f"ERROR on commit: {e}")
        db.rollback()
        raise

    # =========================================================
    # Fill in predictions for future rows ONLY.
    # `after_timestamp=latest_timestamp` guarantees predict_future
    # can never touch rows at or before the real data cutoff —
    # unlike the old implementation, which used wall-clock `now`
    # and could therefore overwrite genuine historical orders.
    # =========================================================
    if MODEL_PATH.exists() and latest_timestamp:
        predict_future(db, after_timestamp=latest_timestamp)

    return {
        "message": "Upload successful",
        "rows_processed": len(records)
    }