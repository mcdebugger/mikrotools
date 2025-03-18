import click

from mikrotools.cli.utils import common_options
from mikrotools.mikromanager import mikromanager_init
from mikrotools.tools.config import get_hosts

from .utils import get_outdated_hosts, list_outdated_hosts, upgrade_hosts_firmware_start, upgrade_hosts_routeros_start

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

@click.command(help='Check for routers with outdated firmware')
@click.argument('min-version')
@click.argument('filtered-version', required=False)
@click.option('-o', '--output-file', required=False)
@mikromanager_init
@common_options
def outdated(min_version, filtered_version, output_file, *args, **kwargs):
    hosts = get_hosts()
    outdated_hosts = get_outdated_hosts(hosts, min_version, filtered_version)
    if output_file:
        with open(output_file, 'w') as output_file:
            for host in outdated_hosts:
                output_file.write(f'{host}\n')
    else:
        list_outdated_hosts(outdated_hosts)

def register(cli_group):
    cli_group.add_command(outdated)
    cli_group.add_command(upgrade)
    cli_group.add_command(upgrade_firmware)
