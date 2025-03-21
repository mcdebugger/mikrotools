import click

from mikrotools.cli.options import common_options
from mikrotools.cli.utils import cli
from mikrotools.mikromanager import mikromanager_init
from mikrotools.tools.config import get_hosts

from .utils import list_hosts

@cli.command(name='list', help='List routers', aliases=['ls'])
@mikromanager_init
@common_options
def list_routers(*args, **kwargs):
    hosts = get_hosts()
    list_hosts(hosts)

def register(cli_group):
    cli_group.add_command(list_routers)
