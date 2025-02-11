#!/usr/bin/env python3

import click

from tools.config import get_commands, get_hosts
from tools.outputs import list_outdated_hosts
from tools.ssh import execute_hosts_commands
from tools.ssh import get_outdated_hosts, get_upgradable_hosts, upgrade_hosts_prompt
from tools.ssh import get_upgradable_hosts_bootloader, upgrade_hosts_bootloader_prompt

@click.group(invoke_without_command=True)
@click.option('-H', '--host')
@click.option('-e', '--execute-command')
@click.option('-i', '--inventory-file')
@click.option('-c', '--config-file', default='settings.yaml')
@click.option('-C', '--commands-file')
@click.pass_context
def cli(ctx, host, execute_command, inventory_file, config_file, commands_file):
    if ctx.invoked_subcommand is None:
        ctx.invoke(exec,
                   host=host,
                   execute_command=execute_command,
                   inventory_file=inventory_file,
                   config_file=config_file,
                   commands_file=commands_file)

@cli.command(help='Execute commands on hosts')
@click.option('-H', '--host')
@click.option('-e', '--execute-command')
@click.option('-i', '--inventory-file')
@click.option('-c', '--config-file', default='settings.yaml')
@click.option('-C', '--commands-file')
def exec(host, execute_command, inventory_file, config_file, commands_file):
    hosts = get_hosts()
    
    # Getting command from arguments or config file
    commands = get_commands()
    
    # Executing commands for each host in list
    execute_hosts_commands(hosts, commands)

@cli.command(help='Check for routers with outdated firmware')
@click.argument('min-version')
@click.argument('filtered-version', required=False)
@click.option('-H', '--host')
@click.option('-i', '--inventory-file')
@click.option('-c', '--config-file', default='settings.yaml')
def outdated(min_version, filtered_version, host, inventory_file, config_file):
    hosts = get_hosts()
    outdated_hosts = get_outdated_hosts(hosts, min_version, filtered_version)
    list_outdated_hosts(outdated_hosts)

@cli.command(help='Upgrade routers with outdated firmware')
@click.option('-H', '--host')
@click.option('-i', '--inventory-file')
@click.option('-c', '--config-file', default='settings.yaml')
def upgrade(host, inventory_file, config_file):
    hosts = get_hosts()
    upgradable_hosts = get_upgradable_hosts(hosts)
    upgrade_hosts_prompt(upgradable_hosts)

@cli.command(help='Upgrade routers with outdated bootloader')
@click.option('-H', '--host')
@click.option('-i', '--inventory-file')
@click.option('-c', '--config-file', default='settings.yaml')
def upgrade_bootloader(host, inventory_file, config_file):
    hosts = get_hosts()
    upgradable_hosts = get_upgradable_hosts_bootloader(hosts)
    upgrade_hosts_bootloader_prompt(upgradable_hosts)

if __name__ == '__main__':
    cli()
