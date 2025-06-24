from typing import TYPE_CHECKING
from backend.schemas.auth_schemas import TokenData
from passlib.context import CryptContext
from typing import Optional, Tuple


if TYPE_CHECKING:
    from backend.db_models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def validate_password_complexity(password: str) -> Tuple[bool, Optional[str]]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    return True, None

def some_service_function(user: 'User'):
    pass


def create_user(email: str, password: str) -> TokenData:
    from backend.core.database import SessionLocal
    from backend.core.security import get_password_hash

    db = SessionLocal()
    try:
        hashed_password = get_password_hash(password)
        return TokenData(email=email)
    finally:
        db.close()