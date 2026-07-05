from sqlalchemy import Column, Integer, DateTime
from app.db.database import Base

class Volume(Base):
    __tablename__ = "volume"

    id        = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, unique=True, index=True)
    orders      = Column(Integer, nullable=False, default=0, server_default="0")
    past_1_hour  = Column(Integer, nullable=False, default=0, server_default="0")
    past_1_day   = Column(Integer, nullable=False, default=0, server_default="0")
    past_1_week  = Column(Integer, nullable=False, default=0, server_default="0")
    past_1_month = Column(Integer, nullable=False, default=0, server_default="0")