import click

from mikrotools.cli.options import common_options
from mikrotools.cli.utils import cli
from mikrotools.mikromanager import mikromanager_init
from mikrotools.tools import coro, get_hosts

from .utils import list_hosts

@cli.command(name='list', help='List routers', aliases=['ls'])
@click.option('-f', '--follow', is_flag=True, default=False)
@mikromanager_init
@common_options
@coro
async def list_routers(follow, *args, **kwargs):
    hosts = get_hosts()
    await list_hosts(hosts, follow=follow)

def register(cli_group):
    cli_group.add_command(list_routers)
