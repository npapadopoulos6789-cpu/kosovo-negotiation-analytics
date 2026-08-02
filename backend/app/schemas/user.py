from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    # EmailStr: το Pydantic ελέγχει ΑΥΤΟΜΑΤΑ ότι αυτό είναι έγκυρη
    # μορφή email (π.χ. "test@test" θα απορριφθεί, "test@test.com" όχι)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.VIEWER


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