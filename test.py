from app.db.database import Base, engine
from app.models.volume import Volume

print("Metadata:", Base.metadata.create_all(bind=engine))
print("Tables:", Base.metadata.tables.keys())