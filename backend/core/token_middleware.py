from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from jose import jwt, JWTError
from backend.core.config import settings
from typing import Optional

logger = logging.getLogger(__name__)

class TokenValidationError(HTTPException):
    def __init__(self, detail: str, status_code: int = 401):
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

EXCLUDED_PATHS = {
    "/", "/auth/login", "/auth/logout", "/auth/me",
    "/docs", "/openapi.json", "/favicon.ico", "/redoc"
}

async def token_validator_middleware(request: Request, call_next):
    if request.url.path in EXCLUDED_PATHS:
        return await call_next(request)

    # Cerca il token in 3 possibili posizioni
    token = (
        request.cookies.get("access_token") or
        request.headers.get("authorization", "").replace("Bearer ", "") or
        request.headers.get("x-access-token", "")
    )

    if not token:
        print("=== ERRORE: TOKEN NON TROVATO ===")
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        request.state.user = payload
        print(f"=== TOKEN VALIDO PER: {payload.get('sub')} ===")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return await call_next(request)

def _extract_token_from_headers(request: Request) -> Optional[str]:
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None

def _validate_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if not payload.get("sub"):
            raise TokenValidationError("Invalid token payload")
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenValidationError("Token expired")
    except JWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise TokenValidationError("Invalid token")