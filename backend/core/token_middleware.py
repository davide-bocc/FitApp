from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class TokenValidationError(HTTPException):
    """Eccezione personalizzata per errori di validazione token"""

    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


async def token_validator_middleware(request: Request, call_next):
    """
    Middleware avanzato per la validazione dei token con:
    - Blocco assoluto di token non standard
    - Validazione JWT rigorosa
    - Protezione contro token legacy
    - Logging dettagliato
    """
    try:
        # 1. Estrazione e pulizia header
        auth_header = request.headers.get("authorization", "").strip()
        logger.debug(f"Inizio validazione token per {request.url.path}")

        # 2. Controllo assoluto per token non consentiti
        forbidden_patterns = [
            r"manual_token",  # Blocca manual_token in qualsiasi forma
            r"Bearer\s+[^eyJ]",  # Blocca token che non iniziano con eyJ
            r"Bearer\s+\S{0,20}",  # Blocca token troppo corti
        ]

        for pattern in forbidden_patterns:
            if re.search(pattern, auth_header, re.IGNORECASE):
                logger.error(f"Token proibito rilevato: {auth_header[:30]}...")
                raise TokenValidationError(
                    "Formato token non consentito",
                    status_code=403
                )

        # 3. Validazione JWT rigorosa
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

            # Verifica struttura JWT di base
            if not re.match(r'^eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*$', token):
                logger.warning(f"Token JWT malformato: {token[:20]}...")
                raise TokenValidationError(
                    "Struttura token JWT non valida",
                    status_code=401
                )

            # Verifica parti del token
            parts = token.split('.')
            if len(parts) != 3:
                raise TokenValidationError(
                    "Token JWT deve avere 3 parti separate",
                    status_code=401
                )

        # 4. Logging differenziato
        if request.url.path not in ["/docs", "/openapi.json", "/favicon.ico"]:
            log_message = f"Accesso a {request.method} {request.url.path}"
            if auth_header:
                log_message += f" | Token: {auth_header[:6]}...{auth_header[-6:]}"
            logger.info(log_message)

        response = await call_next(request)

        # 5. Pulizia header sensibili nella risposta
        sensitive_headers = ["server", "x-powered-by"]
        for header in sensitive_headers:
            if header in response.headers:
                del response.headers[header]

        return response

    except TokenValidationError as tve:
        logger.warning(f"Validazione token fallita: {tve.detail}")
        return JSONResponse(
            status_code=tve.status_code,
            content={
                "error": "token_validation_failed",
                "detail": tve.detail,
                "timestamp": datetime.now().isoformat(),
                "path": request.url.path,
                "suggested_action": "Esegui nuovamente il login"
            }
        )

    except HTTPException as http_exc:
        logger.error(f"Errore HTTP durante la validazione: {http_exc.detail}")
        return JSONResponse(
            status_code=http_exc.status_code,
            content={
                "error": "authentication_error",
                "detail": http_exc.detail,
                "timestamp": datetime.now().isoformat()
            }
        )

    except Exception as exc:
        logger.critical(f"Errore imprevisto nel middleware: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "detail": "Errore durante la validazione del token",
                "timestamp": datetime.now().isoformat()
            }
        )