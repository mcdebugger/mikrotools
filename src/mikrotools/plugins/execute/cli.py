import click

from mikrotools.cli.utils import common_options, Mutex
from mikrotools.mikromanager import mikromanager_init
from mikrotools.tools.config import get_hosts, get_commands

from .utils import execute_hosts_commands

@click.command(name='exec', help='Execute commands on hosts')
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

def register(cli_group):
    cli_group.add_command(execute)
