import logging
from typing import Any, Callable

type Data = dict[str, Any]
type ExportFn = Callable[[Data], None]
logger = logging.getLogger(__name__)

logger.handlers.clear()
logging.basicConfig(
    format="%(asctime)s - %(levelname)s  - %(name)s - %(funcName)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

loggers: dict[str, ExportFn] = {
    """
    This is my dynamic function switching pattern. I didn't realize that it was called the Registry pattern.
    """
    'info': logger.info,
    'warn': logger.warning,
    'error': logger.error,
    'debug': logger.debug
}
