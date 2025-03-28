import asyncio
import click

from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup

from mikrotools.cli.options import common_options
from mikrotools.mikromanager import mikromanager_init
from mikrotools.tools.config import get_hosts, get_commands

from .utils import execute_hosts_commands

@click.command(name='exec', help='Execute commands on hosts')
@optgroup.group('Commands to execute', cls=RequiredMutuallyExclusiveOptionGroup)
@optgroup.option('-e', '--execute-command')
@optgroup.option('-C', '--commands-file', type=click.Path(exists=True))
@mikromanager_init
@common_options
def execute(*args, **kwargs):
    addresses = get_hosts()
    
    # Getting command from arguments or config file
    commands = get_commands()
    
    # Executing commands for each host in list
    asyncio.run(execute_hosts_commands(addresses, commands))

def register(cli_group):
    cli_group.add_command(execute)
