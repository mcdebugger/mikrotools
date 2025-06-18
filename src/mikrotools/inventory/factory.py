import logging
import os

from mikrotools.config.models import InventorySourceConfig
from mikrotools.inventory.providers import FileInventorySource, NetboxInventorySource, SingleInventorySource, StaticInventorySource
from mikrotools.inventory.protocol import InventorySource

logger = logging.getLogger(__name__)

def get_inventory_source(config: InventorySourceConfig | None = None, source: str | None = None) -> InventorySource:
    if config is not None:
        if config.type == 'file' and config.path is not None:
            logger.debug(f'get_inventory_source: Inventory source is a file: {config.file}')
            return FileInventorySource(config.path)
        elif config.type == 'netbox':
            if config.token is None:
                raise ValueError('Netbox token is not specified')
            if config.url is None:
                raise ValueError('Netbox URL is not specified')
            logger.debug(f'get_inventory_source: Inventory source is a Netbox: {config.url}')
            return NetboxInventorySource(config.url, config.token, config.filters)
        elif config.type == 'static' and config.hosts is not None:
            logger.debug(f'get_inventory_source: Inventory source is a static list of hosts: {config.hosts}')
            return StaticInventorySource(config.hosts)
        else:
            raise ValueError(f'Unknown inventory source type: {config.type}')
    elif source is not None:
        if os.path.isfile(source):
            logger.debug(f'get_inventory_source: Inventory source is a file: {source}')
            return FileInventorySource(source)
        else:
            logger.debug(f'get_inventory_source: Inventory source is a single host: {source}')
            return SingleInventorySource(source)
    else:
        raise ValueError('Inventory source is not specified')