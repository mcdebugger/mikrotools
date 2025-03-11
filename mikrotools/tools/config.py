import click
import logging

from mikrotools.config import get_config

logger = logging.getLogger(__name__)

def get_commands():
    ctx = click.get_current_context()

    if ctx.params['execute_command']:
        commands = [ctx.params['execute_command']]
    elif ctx.params['commands_file']:
        commands = get_commands_from_file(ctx.params['commands_file'])
    else:
        commands = []
    
    return commands

def get_commands_from_file(filename):
    with open(filename) as commands_file:
        commands = [command.rstrip() for command in commands_file]
        return commands

def get_hosts():
    ctx = click.get_current_context()
    if ctx.params['host']:
        hosts = [ctx.params['host']]
    elif ctx.params['inventory_file']:
        logger.debug(f'get_hosts: Inventory file path set from command line: '
                     f'{ctx.params["inventory_file"]}')
        try:
            hosts = read_hosts_from_file(ctx.params['inventory_file'])
        except TypeError:
            logger.error('Inventory file or host address is not specified')
            exit(1)
        except FileNotFoundError:
            logger.error(f'Inventory file not found: {ctx.params["inventory_file"]}')
            exit(1)
    else:
        # Getting config from YAML file
        config = get_config()
        logger.debug(f'get_hosts: Config: {config}')
        logger.debug(f'get_hosts: Inventory file path set from config: '
                     f'{config.inventory.hostsFile}')
        try:
            hosts = read_hosts_from_file(config.inventory.hostsFile)
        except TypeError:
            logger.error('Inventory file or host address is not specified')
            exit(1)
        except FileNotFoundError:
            logger.error(f'Inventory file not found: {config.inventory.hostsFile}')
            exit(1)
    
    return hosts

def read_hosts_from_file(filename):
    with open(filename) as hostsfile:
        hosts = [host.rstrip() for host in hostsfile]
        return hosts
