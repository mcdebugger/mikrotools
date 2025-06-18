import logging
import os

from mikrotools.inventory.providers import FileInventorySource, SingleInventorySource
from mikrotools.inventory.protocol import InventorySource

logger = logging.getLogger(__name__)

def get_inventory_source(source: str) -> InventorySource:
    if os.path.isfile(source):
        logger.debug(f'get_inventory_source: Inventory source is a file: {source}')
        return FileInventorySource(source)
    else:
        logger.debug(f'get_inventory_source: Inventory source is a single host: {source}')
        return SingleInventorySource(source)