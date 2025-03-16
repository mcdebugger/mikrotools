#!/usr/bin/env python3

import click
import logging

from functools import wraps

from .config import get_config, load_config
from .tools.config import get_commands, get_hosts
from .tools.outputs import list_outdated_hosts
from .tools.ssh import execute_hosts_commands
from .tools.ssh import get_outdated_hosts
from .hoststools import backup_configs
from .hoststools.common import list_hosts, reboot_addresses
from .hoststools.upgrade import upgrade_hosts_firmware_start, upgrade_hosts_routeros_start
from .netapi import MikrotikManager

class Mutex(click.Option):
    def __init__(self, *args, **kwargs):
        self.not_required_if:list = kwargs.pop("not_required_if")

        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs["help"] = (kwargs.get("help", "") + "Option is mutually exclusive with " + ", ".join(self.not_required_if) + ".").strip()
        super(Mutex, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        current_opt:bool = self.name in opts
        for mutex_opt in self.not_required_if:
            if mutex_opt in opts:
                if current_opt:
                    raise click.UsageError("Illegal usage: '" + str(self.name) + "' is mutually exclusive with " + str(mutex_opt) + ".")
                else:
                    self.required = False
        return super(Mutex, self).handle_parse_result(ctx, opts, args)

def common_options(func):
    @click.option('-H', '--host', help='Target host')
    @click.option('-P', '--port', type=int, help='SSH port')
    @click.option('-u', '--user', help='Username')
    @click.option('-p', '--password', is_flag=True, help='Prompt for password')
    @click.option('-c', '--config-file')
    @click.option('-i', '--inventory-file')
    @click.option('-j', '--jump', is_flag=True, help='Use jump host')
    @click.option('-d', '--debug', is_flag=True, help='Enable debug mode')
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def mikromanager_init(f):
    @wraps(f)
    def wrapper(port, user, password, config_file, inventory_file, jump, *args, **kwargs):
        logger = logging.getLogger(__name__)
        try:
            config = load_config(config_file)
        except Exception as e:
            logger.error(f'Failed to load config file: {e}')
            exit(1)
    
        if port is not None:
            config.ssh.port = int(port)
        if user is not None:
            config.ssh.username = user
        if password:
            config.ssh.keyfile = None
            # Password prompt
            config.ssh.password = click.prompt('Password', hide_input=True)
        if inventory_file is not None:
            config.inventory.hostsFile = inventory_file
        if jump:
            config.ssh.jump = True
        
        logger.debug(f'Config after applying command line options: {config}')
        
        # Configuring MikrotikManager
        MikrotikManager.configure(config)
        
        return f(*args, **kwargs)
    
    return wrapper

def setup_logging(debug):
    if debug:
        level = logging.DEBUG
    else:
        level = logging.WARNING
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def validate_commands(ctx, param, values):
    execute_command = ctx.params.get('execute_command')
    commands_file = ctx.params.get('commands_file')
    
    if (not execute_command and not commands_file):
        raise click.UsageError('You must provide either -e or -C')
    
    if (execute_command and commands_file):
        raise click.UsageError('You must provide either -e or -C, but not both.')
    
    return values

@click.group(invoke_without_command=True, context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-e', '--execute-command', cls=Mutex, not_required_if=['commands_file'])
@click.option('-C', '--commands-file', cls=Mutex, not_required_if=['execute_command'])
@common_options
@click.pass_context
def cli(ctx, *args, **kwargs):
    # Setting up logging
    setup_logging(ctx.params['debug'])
    
    # Invoking default command
    if ctx.invoked_subcommand is None:
        validate_commands(ctx, None, None)
        ctx.invoke(execute, *args, **kwargs)

@cli.command(help='Backup configs from hosts')
@click.option('-s', '--sensitive', is_flag=True, default=False)
@mikromanager_init
@common_options
def backup(sensitive, *args, **kwargs):
    hosts = get_hosts()
    backup_configs(hosts, sensitive)

@cli.command(name='exec', help='Execute commands on hosts')
@click.option('-e', '--execute-command', cls=Mutex, not_required_if=['commands_file'])
@click.option('-C', '--commands-file', cls=Mutex, not_required_if=['execute_command'])
@mikromanager_init
@common_options
def execute(*args, **kwargs):
    hosts = get_hosts()
    
    # Getting command from arguments or config file
    commands = get_commands()
    
    # Executing commands for each host in list
    execute_hosts_commands(hosts, commands)

@cli.command(help='Check for routers with outdated firmware')
@click.argument('min-version')
@click.argument('filtered-version', required=False)
@click.option('-o', '--output-file', required=False)
@mikromanager_init
@common_options
def outdated(min_version, filtered_version, output_file, *args, **kwargs):
    hosts = get_hosts()
    outdated_hosts = get_outdated_hosts(hosts, min_version, filtered_version)
    if output_file:
        with open(output_file, 'w') as output_file:
            for host in outdated_hosts:
                output_file.write(f'{host}\n')
    else:
        list_outdated_hosts(outdated_hosts)

@cli.command(name='list', help='List routers')
@mikromanager_init
@common_options
def list_routers(*args, **kwargs):
    hosts = get_hosts()
    list_hosts(hosts)

@cli.command(help='Reboot routers')
@mikromanager_init
@common_options
def reboot(*args, **kwargs):
    addresses = get_hosts()
    reboot_addresses(addresses)

@cli.command(help='Upgrade routers with outdated RouterOS')
@mikromanager_init
@common_options
def upgrade(*args, **kwargs):
    hosts = get_hosts()
    upgrade_hosts_routeros_start(hosts)

@cli.command(help='Upgrade routers with outdated firmware')
@mikromanager_init
@common_options
def upgrade_firmware(*args, **kwargs):
    hosts = get_hosts()
    upgrade_hosts_firmware_start(hosts)

if __name__ == '__main__':
    cli()
