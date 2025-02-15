import click
import yaml

from dataclasses import dataclass

from tools.args import parse_args

@dataclass(frozen=False)
class Config:
    port: int
    user: str
    password: str = None
    keyfile: str = None
    inventory_file: str = None

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

def get_config():
    ctx = click.get_current_context()
    if ctx.params['config_file']:
        path = ctx.params['config_file']
    else:
        path = 'settings.yaml'
    
    # Getting config from YAML file
    yaml_data = load_cfg_from_file(path)
    
    return yaml_data

def load_config(path) -> Config:
    yaml_data = load_cfg_from_file(path)
    config = Config(
        port=yaml_data['Port'],
        user=yaml_data['User'],
        keyfile=yaml_data['KeyFile'],
        inventory_file=yaml_data['HostsFile']
    )
    return config

def get_hosts():
    ctx = click.get_current_context()
    if ctx.params['host']:
        hosts = [ctx.params['host']]
    elif ctx.params['inventory_file']:
        hosts = read_hosts_from_file(ctx.params['inventory_file'])
    else:
        # Getting config from YAML file
        cfg = get_config()
        hostsfile = cfg['HostsFile']
        hosts = read_hosts_from_file(hostsfile)
    
    return hosts

def read_hosts_from_file(filename):
    with open(filename) as hostsfile:
        hosts = [host.rstrip() for host in hostsfile]
        return hosts

def load_cfg_from_file(filename):
    with open(filename) as cfgfile:
        cfg = yaml.safe_load(cfgfile)
        return cfg
