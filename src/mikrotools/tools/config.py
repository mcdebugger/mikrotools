import click
import logging

from mikrotools.config import get_config, InventorySourceConfig
from mikrotools.inventory import get_inventory_source, InventoryItem

logger = logging.getLogger(__name__)

def get_commands():
    ctx = click.get_current_context()

    if ctx.params['execute_command']:
        return [ctx.params['execute_command']]
    elif ctx.params['commands_file']:
        return get_commands_from_file(ctx.params['commands_file'])
    else:
        return []

def get_commands_from_file(filename):
    with open(filename) as commands_file:
        return [command.rstrip() for command in commands_file]

def get_hosts() -> list[InventoryItem]:
    ctx = click.get_current_context()
    if ctx.params['host']:
        invsource = get_inventory_source(source=ctx.params['host'])
    elif ctx.params['inventory_file']:
        invsource = get_inventory_source(config=
            InventorySourceConfig(type='file', path=ctx.params['inventory_file'])
        )
    else:
        # Getting config from YAML file
        config = get_config()
        if config.inventory.sources:
            logger.debug(f'get_hosts: Config: {config}')
            logger.debug(f'get_hosts: Inventory sources set from config: '
                        f'{config.inventory.sources}')
            invsource = get_inventory_source(config=config.inventory.sources[0])
        elif config.inventory.hostsFile:
            logger.debug(f'get_hosts: Config: {config}')
            logger.debug(f'get_hosts: Inventory file path set from config: '
                        f'{config.inventory.hostsFile}')
            invsource = get_inventory_source(source=config.inventory.hostsFile)
        else:
            logger.error('Inventory source is not specified')
            raise click.UsageError('Inventory source or host is not specified')
    
    return invsource.get_hosts()
