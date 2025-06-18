import click
import logging

from mikrotools.config import get_config
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
        invsource = get_inventory_source(ctx.params['host'])
    elif ctx.params['inventory_source']:
        invsource = get_inventory_source(ctx.params['inventory_source'])
    else:
        # Getting config from YAML file
        config = get_config()
        if not config.inventory.hostsFile:
            logger.error('Inventory source is not specified')
            raise click.UsageError('Inventory source or host is not specified')
        logger.debug(f'get_hosts: Config: {config}')
        logger.debug(f'get_hosts: Inventory file path set from config: '
                     f'{config.inventory.hostsFile}')
        invsource = get_inventory_source(config.inventory.hostsFile)
    
    return invsource.get_hosts()
    
    # elif ctx.params['inventory_source']:
    #     logger.debug(f'get_hosts: Inventory source set from command line: '
    #                  f'{ctx.params["inventory_source"]}')
    #     try:
    #         hosts = read_hosts_from_file(ctx.params['inventory_file'])
    #     except TypeError:
    #         logger.error('Inventory file or host address is not specified')
    #         exit(1)
    #     except FileNotFoundError:
    #         logger.error(f'Inventory file not found: {ctx.params["inventory_file"]}')
    #         exit(1)
    # else:
    #     # Getting config from YAML file
    #     config = get_config()
    #     logger.debug(f'get_hosts: Config: {config}')
    #     logger.debug(f'get_hosts: Inventory file path set from config: '
    #                  f'{config.inventory.hostsFile}')
    #     try:
    #         hosts = read_hosts_from_file(config.inventory.hostsFile)
    #     except TypeError:
    #         logger.error('Inventory file or host address is not specified')
    #         exit(1)
    #     except FileNotFoundError:
    #         logger.error(f'Inventory file not found: {config.inventory.hostsFile}')
    #         exit(1)
    
    # return hosts

def read_hosts_from_file(filename):
    with open(filename) as hostsfile:
        return [host.rstrip() for host in hostsfile if not host.startswith('#')]
