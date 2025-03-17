import click

from mikrotools.cli.utils import common_options
from mikrotools.hoststools.common import reboot_addresses
from mikrotools.mikromanager import mikromanager_init
from mikrotools.tools.config import get_hosts

@click.command(help='Reboot routers')
@mikromanager_init
@common_options
def reboot(*args, **kwargs):
    addresses = get_hosts()
    reboot_addresses(addresses)

def register(cli_group):
    cli_group.add_command(reboot)
