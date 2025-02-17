import click
import yaml

from dataclasses import dataclass

from tools.args import parse_args

@dataclass
class JumpHost:
    address: str
    port: int
    username: str
    password: str = None
    keyfile: str = None

@dataclass
class SSHConfig:
    port: int
    username: str
    password: str = None
    keyfile: str = None
    jump: bool = False
    jumphost: JumpHost = None

@dataclass(frozen=False)
class Config:
    ssh: SSHConfig
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

def load_config(path) -> Config:
    yaml_data = load_cfg_from_file(path)
    config = Config(
        inventory_file=yaml_data['inventory']['hosts-file'],
        ssh=SSHConfig(
            port=yaml_data['ssh']['port'],
            username=yaml_data['ssh']['user'],
            keyfile=yaml_data['ssh']['keyfile']
        )
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
        config = load_config(ctx.params['config_file'])
        hosts = read_hosts_from_file(config.inventory_file)
    
    return hosts

def read_hosts_from_file(filename):
    with open(filename) as hostsfile:
        hosts = [host.rstrip() for host in hostsfile]
        return hosts

def load_cfg_from_file(filename):
    with open(filename) as cfgfile:
        cfg = yaml.safe_load(cfgfile)
        return cfg
