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
    logger.debug(f"Incoming cookies: {request.cookies}")
    logger.debug(f"Incoming headers: {dict(request.headers)}")
    # Skip validation for excluded paths
    if request.url.path in EXCLUDED_PATHS:
        logger.debug(f"Bypassing token validation for {request.url.path}")
        return await call_next(request)

    try:
        # Try to get token from cookies or headers
        token = request.cookies.get("access_token") or _extract_token_from_headers(request)
        if not token:
            logger.warning("Token not found in cookies or headers")
            raise TokenValidationError("Authentication required")

        # Validate token and attach user to request
        request.state.user = _validate_jwt(token)
        logger.debug(f"Authenticated user: {request.state.user.get('sub')}")

        return await call_next(request)

    except TokenValidationError as e:
        logger.warning(f"Token validation failed: {e.detail}")
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail},
            headers=e.headers
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
            headers={"WWW-Authenticate": "Bearer"}
        )

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