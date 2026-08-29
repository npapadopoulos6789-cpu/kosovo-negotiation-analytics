from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    # EmailStr: το Pydantic ελέγχει ΑΥΤΟΜΑΤΑ ότι αυτό είναι έγκυρη
    # μορφή email (π.χ. "test@test" θα απορριφθεί, "test@test.com" όχι)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.VIEWER

    # ΠΡΟΣΟΧΗ: αυτό το schema (με role) ΔΕΝ είναι το public register
    # request schema -- βλ. UserRegister παρακάτω. Το UserCreate το
    # χρησιμοποιούν ΜΟΝΟ trusted, μη-HTTP callers (seed script, tests),
    # που αποφασίζουν τα ίδια το role. Ο router POST /auth/register δεν
    # δέχεται ΠΟΤΕ UserCreate απευθείας από το request body.


class UserRegister(BaseModel):
    """
    Request schema του public POST /auth/register. Σκόπιμα ΔΕΝ έχει
    πεδίο "role" -- ένας client δεν μπορεί να το στείλει καν, ό,τι extra
    key στείλει (π.χ. "role": "ADMIN") αγνοείται σιωπηλά από το Pydantic
    (default extra="ignore"). Ο service layer (register_public_user)
    βάζει ΠΑΝΤΑ VIEWER, χωρίς εξαίρεση -- ο μοναδικός τρόπος να υπάρξει
    ADMIN είναι το seed script (ADMIN_EMAIL/ADMIN_PASSWORD).
    """

    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: UserRole
    # ΠΡΟΣΕΞΕ: δεν υπάρχει hashed_password εδώ -- ΠΟΤΕ δεν επιστρέφουμε
    # το password (ούτε καν το hash του) πίσω στον client


class Token(BaseModel):
    # Αυτό επιστρέφουμε μετά από επιτυχές login
    access_token: str
    token_type: str = "bearer"