from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.repositories import user as user_repository
from app.models.user import User, UserRole

# Λέει στο FastAPI "τα tokens έρχονται μέσω του /auth/login endpoint"
# -- αυτό χρησιμοποιείται κυρίως για να εμφανίζεται σωστά το κουμπί
# "Authorize" στο Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
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

    payload = decode_access_token(token)
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
