import asyncio
import click

from mikrotools.cli.options import common_options
from mikrotools.hoststools import reboot_addresses
from mikrotools.mikromanager import mikromanager_init
from mikrotools.tools.config import get_hosts

@click.command(help='Reboot routers')
@mikromanager_init
@common_options
def reboot(*args, **kwargs):
    addresses = get_hosts()
    asyncio.run(reboot_addresses(addresses))

def register(cli_group):
    cli_group.add_command(reboot)
