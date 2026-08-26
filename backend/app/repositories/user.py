from sqlalchemy.orm import Session

from app.models.user import User, UserRole


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_by_email(db: Session, email: str) -> User | None:
    # Θα το χρησιμοποιήσουμε ΣΥΧΝΑ -- κάθε φορά που κάποιος κάνει login,
    # ψάχνουμε τον χρήστη με βάση το email του
    return db.query(User).filter(User.email == email).first()


def get_by_role(db: Session, role: UserRole) -> User | None:
    # Χρησιμοποιείται από το seed script για το idempotency check του
    # αρχικού ADMIN χρήστη -- "υπάρχει ήδη έστω ένας;"
    return db.query(User).filter(User.role == role).first()


def create(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user