from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.repositories import user as user_repository
from app.models.user import User, UserRole

# HTTPBearer αντί για OAuth2PasswordBearer -- το δικό μας login (POST
# /auth/login) είναι απλό JSON body, όχι OAuth2 form grant, οπότε το
# OAuth2PasswordBearer έκανε το Swagger UI "Authorize" dialog να ζητάει
# username/password/client_id πεδία που δεν χρησιμοποιούνται ποτέ και δεν
# δούλευαν όταν συμπληρώνονταν. Το HTTPBearer δίνει ένα απλό πεδίο "Value"
# όπου επικολλάς το access_token απευθείας.
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Παίρνει το token από το request, το επαληθεύει, και επιστρέφει
    τον αντίστοιχο χρήστη. Αν κάτι πάει στραβά, σταματάει το request
    με 401 πριν καν φτάσει στο endpoint.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    email = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = user_repository.get_by_email(db, email)
    if user is None:
        raise credentials_exception

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Ίδιο με το get_current_user, ΑΛΛΑ επιπλέον ελέγχει ότι ο χρήστης
    είναι ADMIN -- αλλιώς 403 Forbidden.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires ADMIN privileges",
        )
    return current_user
