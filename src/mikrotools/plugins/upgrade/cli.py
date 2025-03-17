import click

from mikrotools.cli.utils import common_options
from mikrotools.hoststools.upgrade import upgrade_hosts_firmware_start, upgrade_hosts_routeros_start
from mikrotools.mikromanager import mikromanager_init
from mikrotools.tools.config import get_hosts

@click.command(help='Upgrade routers with outdated RouterOS')
@mikromanager_init
@common_options
def upgrade(*args, **kwargs):
    hosts = get_hosts()
    upgrade_hosts_routeros_start(hosts)

@click.command(help='Upgrade routers with outdated firmware')
@mikromanager_init
@common_options
def upgrade_firmware(*args, **kwargs):
    hosts = get_hosts()
    upgrade_hosts_firmware_start(hosts)

def register(cli_group):
    cli_group.add_command(upgrade)
    cli_group.add_command(upgrade_firmware)
