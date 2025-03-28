import logging

from mikrotools.hoststools import cleanup_connections

__all__ = ['cleanup_all']

logger = logging.getLogger(__name__)

def cleanup_all() -> None:
    logger.debug('Cleaning up')
    cleanup_connections()
