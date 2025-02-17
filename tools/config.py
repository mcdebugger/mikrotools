import click
import logging
import yaml

from pydantic import BaseModel

logger = logging.getLogger(__name__)

class Base (BaseModel):
    pass

class Inventory(Base):
    hostsFile: str = None

class JumpHost(Base):
    address: str = None
    port: int = 22
    username: str = None
    password: str = None
    keyfile: str = None

class SSHConfig(Base):
    port: int = 22
    username: str = None
    password: str = None
    keyfile: str = None
    jump: bool = False
    jumphost: JumpHost = JumpHost()

class Config(Base):
    ssh: SSHConfig = SSHConfig()
    inventory: Inventory = Inventory()

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

def load_config(path) -> Config:
    try:
        yaml_data = load_cfg_from_file(path)
    except FileNotFoundError:
        logger.warning(f'Config file not found: {path}')
        yaml_data = None
    
    if yaml_data is not None:
        config = Config(**yaml_data)
    else:
        config = Config()
        
    logger.debug(f'Config loaded from YAML: {config}')
    return config

def get_hosts():
    ctx = click.get_current_context()
    if ctx.params['host']:
        hosts = [ctx.params['host']]
    elif ctx.params['inventory_file']:
        hosts = read_hosts_from_file(ctx.params['inventory_file'])
    else:
        # Getting config from YAML file
        config = load_config(ctx.params['config_file'])
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

def load_cfg_from_file(filename):
    with open(filename) as cfgfile:
        cfg = yaml.safe_load(cfgfile)
        return cfg
