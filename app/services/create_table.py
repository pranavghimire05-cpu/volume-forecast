from app.db.database import engine, Base
from app.models.performance import Performance

Base.metadata.create_all(bind=engine)

print("Tables created")