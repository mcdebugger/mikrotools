import asyncio
import click

from mikrotools.cli.options import common_options
from mikrotools.mikromanager import mikromanager_init
from mikrotools.tools.config import get_hosts

from .utils import backup_configs

@click.command(help='Backup configs from hosts')
@click.option('-s', '--sensitive', is_flag=True, default=False)
@mikromanager_init
@common_options
def backup(sensitive, *args, **kwargs):
    hosts = get_hosts()
    asyncio.run(backup_configs(hosts, sensitive))

def register(cli_group):
    cli_group.add_command(backup)
