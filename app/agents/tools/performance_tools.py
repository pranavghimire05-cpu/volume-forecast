from langchain_core.tools import tool
from app.db.database import SessionLocal
from app.services.performance.performance_query import get_all_performance_rows

@tool
def read_all_performance(limit: int = 1000):
    """
    Reads all rows from performance table (with safety limit).
    """

    db = SessionLocal()
    try:
        return get_all_performance_rows(db, limit)
    finally:
        db.close()