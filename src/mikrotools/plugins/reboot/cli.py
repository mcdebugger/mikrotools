import click

from mikrotools.cli.options import common_options
from mikrotools.hoststools import reboot_addresses
from mikrotools.mikromanager import mikromanager_init
from mikrotools.tools import coro, get_hosts

@click.command(help='Reboot routers')
@mikromanager_init
@common_options
@coro
async def reboot(*args, **kwargs):
    addresses = get_hosts()
    await reboot_addresses(addresses)

def register(cli_group):
    cli_group.add_command(reboot)
