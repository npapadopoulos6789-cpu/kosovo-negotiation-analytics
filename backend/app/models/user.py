from sqlalchemy import Column, Integer, String, Enum
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    VIEWER = "VIEWER"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # unique=True: δεν επιτρέπονται δύο χρήστες με το ίδιο email
    email = Column(String(200), unique=True, nullable=False, index=True)

    # ΠΟΤΕ δεν αποθηκεύουμε τον πραγματικό κωδικό -- μόνο το hash του
    hashed_password = Column(String(200), nullable=False)

    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)