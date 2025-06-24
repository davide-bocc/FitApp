from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Riceve una password in chiaro e restituisce la versione hashed con bcrypt.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica che la password in chiaro corrisponda a quella hashed.
    """
    return pwd_context.verify(plain_password, hashed_password)
