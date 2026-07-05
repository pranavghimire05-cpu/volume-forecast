from sqlalchemy import Column, Integer, String, Float

from app.db.database import Base


class Performance(Base):
    __tablename__ = "performance"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    mph = Column(Float, nullable=True)      # Maps Per Hour / Analyzed Per Hour
    rph = Column(Float, nullable=True)      # Reviews Per Hour

    role = Column(String, nullable=False)   # analyst / reviewer

    accuracy = Column(Float, nullable=True) # 0-100

    rating = Column(Float, nullable=True)   # Calculated score