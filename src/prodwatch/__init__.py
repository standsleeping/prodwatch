import os
from .manager import Manager
from .exceptions import TokenError
from .logging_config import configure_logging, get_logger

DEFAULT_BASE_SERVER_URL = "https://getprodwatch.com"
DEFAULT_LOG_LEVEL = "INFO"


def start_prodwatch(app_name: str) -> None:
    logger = None
    try:
        log_level = os.getenv("PRODWATCH_LOG_LEVEL", DEFAULT_LOG_LEVEL)

        configure_logging(log_level)

        logger = get_logger(__name__)

        base_server_url = os.getenv("PRODWATCH_API_URL", DEFAULT_BASE_SERVER_URL)

        manager = Manager(base_server_url, app_name=app_name)

        if not manager.check_connection():
            return

        manager.start()
    except TokenError as e:
        if logger:
            logger.error(f"Token Error: {e}")
            logger.error("Prodwatch monitoring disabled.")
        return
