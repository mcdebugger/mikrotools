import click
import yaml

from tools.args import parse_args

def get_commands():
    ctx = click.get_current_context()

    if ctx.params['execute_command']:
        commands = [ctx.params['execute_command']]
    elif ctx.params['commands_file']:
        commands = get_commands_from_file(ctx.params['commands_file'])
    else:
        # Getting config from YAML file
        cfg = get_config()
        commands = [cfg['Command']]
    
    return commands

def get_commands_from_file(filename):
    with open(filename) as commands_file:
        commands = [command.rstrip() for command in commands_file]
        return commands

def get_config():
    ctx = click.get_current_context()
    if ctx.params['config_file']:
        filename = ctx.params['config_file']
    else:
        filename = 'settings.yaml'
    
    # Getting config from YAML file
    cfg = load_cfg_from_file(filename)
    
    return cfg

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
