from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import DATABASE_URL

# Το "engine" ξέρει ΠΩΣ να συνδεθεί με τη ΒΔ
engine = create_engine(DATABASE_URL)

# "Εργοστάσιο" που φτιάχνει sessions -- κάθε session είναι μια
# συνομιλία με τη ΒΔ (πάρε/αποθήκευσε δεδομένα)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Η βασική κλάση από την οποία θα κληρονομούν όλα τα models μας
class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()