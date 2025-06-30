import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
import sys
from backend.core.config import settings


class SecurityFilter(logging.Filter):
    """Filtro per dati sensibili"""

    def filter(self, record):
        sensitive = ['password', 'token', 'secret', 'authorization']
        msg = str(getattr(record, 'msg', ''))
        for word in sensitive:
            if word.lower() in msg.lower():
                record.msg = f"[REDACTED] {msg.split(word)[0]}...[sensitive]"
                break
        return True


def setup_logger():
    """Configurazione logger avanzata"""
    logger = logging.getLogger(__name__)
    logger.setLevel(settings.LOG_LEVEL)

    # Formattazione
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s'
    )

    # Console Handler (solo errori in produzione)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if settings.DEV_MODE else logging.INFO)
    if settings.LOG_SENSITIVE_FILTER:
        console_handler.addFilter(SecurityFilter())
    logger.addHandler(console_handler)

    # File Handler con rotazione
    if settings.LOG_FILE:
        log_path = Path(settings.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    return logger


# Logger principale
logger = setup_logger()

# Logger specializzato per auth
auth_logger = logging.getLogger('backend.auth')
auth_logger.propagate = True

# Utility per logging strutturato
def log_auth_attempt(**kwargs):
    """Log strutturato per tentativi di autenticazione"""
    logger.info(
        "Auth attempt | IP: %s | User: %s | Status: %s",
        kwargs.get('ip', 'unknown'),
        kwargs.get('username', 'unknown'),
        kwargs.get('status', 'attempt'),
        extra={'type': 'AUTH', **kwargs}
    )


def log_token_validation(token_prefix, is_valid):
    """Log specifico per validazione token"""
    logger.debug(
        "Token validation | Prefix: %s... | Valid: %s",
        token_prefix[:6],
        is_valid,
        extra={'type': 'TOKEN_VALIDATION'}
    )