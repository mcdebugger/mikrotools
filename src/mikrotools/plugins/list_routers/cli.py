import asyncio
import click

from mikrotools.cli.options import common_options
from mikrotools.cli.utils import cli
from mikrotools.mikromanager import mikromanager_init
from mikrotools.tools.config import get_hosts

from .utils import list_hosts

@cli.command(name='list', help='List routers', aliases=['ls'])
@click.option('-f', '--follow', is_flag=True, default=False)
@mikromanager_init
@common_options
def list_routers(follow, *args, **kwargs):
    hosts = get_hosts()
    asyncio.run(list_hosts(hosts, follow=follow))

def register(cli_group):
    cli_group.add_command(list_routers)
