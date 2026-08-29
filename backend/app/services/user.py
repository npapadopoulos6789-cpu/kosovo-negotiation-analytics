from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.repositories import user as user_repository
from app.schemas.user import UserCreate, UserRegister
from app.core.security import hash_password, verify_password, create_access_token


class EmailAlreadyRegisteredError(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Email '{email}' is already registered")


class InvalidCredentialsError(Exception):
    def __init__(self):
        super().__init__("Invalid email or password")


def register_user(db: Session, data: UserCreate) -> User:
    # Business rule: δεν επιτρέπονται δύο χρήστες με το ίδιο email
    if user_repository.get_by_email(db, data.email) is not None:
        raise EmailAlreadyRegisteredError(data.email)

    # ΕΔΩ γίνεται το hashing -- ο πραγματικός κωδικός (data.password)
    # ΔΕΝ αποθηκεύεται ποτέ, μόνο το hash του
    new_user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
    )
    return user_repository.create(db, new_user)


def register_public_user(db: Session, data: UserRegister) -> User:
    """
    Self-service registration -- ο μοναδικός caller είναι το POST
    /auth/register. Το role ΕΙΝΑΙ ΠΑΝΤΑ VIEWER, hardcoded εδώ, ΠΟΤΕ από
    το request body (το UserRegister schema δεν έχει καν πεδίο role,
    βλ. schemas/user.py). Καμία δημόσια διαδρομή προαγωγής σε ADMIN --
    ο μοναδικός τρόπος να υπάρξει ADMIN είναι το seed script
    (ADMIN_EMAIL/ADMIN_PASSWORD) μέσω του register_user παραπάνω.
    """
    return register_user(
        db,
        UserCreate(email=data.email, password=data.password, role=UserRole.VIEWER),
    )


def authenticate_user(db: Session, email: str, password: str) -> str:
    """
    Ελέγχει τα στοιχεία login, και αν είναι σωστά, επιστρέφει ένα
    JWT access token.
    """
    user = user_repository.get_by_email(db, email)

    # ΠΡΟΣΟΧΗ: ελέγχουμε "ο χρήστης δεν υπάρχει" ΚΑΙ "λάθος κωδικός"
    # με το ΙΔΙΟ ακριβώς μήνυμα σφάλματος (InvalidCredentialsError).
    # Αυτό είναι ΣΚΟΠΙΜΟ -- αν λέγαμε ξεχωριστά "ο χρήστης δεν υπάρχει"
    # vs "λάθος κωδικός", θα δίναμε σε επίδοξους εισβολείς την
    # πληροφορία "ποια emails υπάρχουν πραγματικά" στο σύστημα.
    if user is None or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError()

    # Το access token περιέχει το email και τον ρόλο του χρήστη -- θα τα
    # χρησιμοποιήσουμε αργότερα για να ξέρουμε "ποιος είναι" και "τι
    # επιτρέπεται να κάνει" σε κάθε επόμενο request
    token = create_access_token(data={"sub": user.email, "role": user.role.value})
    return token