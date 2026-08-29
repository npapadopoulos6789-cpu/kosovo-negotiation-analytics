from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import user as user_service
from app.schemas.user import UserRegister, UserLogin, UserRead, Token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    # UserRegister (ΟΧΙ UserCreate) -- δεν έχει καν πεδίο "role", άρα δεν
    # υπάρχει καμία δυνατότητα ο client να επιλέξει το δικό του role εδώ.
    # register_public_user βάζει ΠΑΝΤΑ VIEWER, βλ. services/user.py.
    return user_service.register_public_user(db, payload)


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    token = user_service.authenticate_user(db, payload.email, payload.password)
    return Token(access_token=token)