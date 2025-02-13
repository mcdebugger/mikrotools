#!/usr/bin/env python3

import click

from tools.config import get_commands, get_hosts
from tools.outputs import list_outdated_hosts
from tools.ssh import execute_hosts_commands
from tools.ssh import get_outdated_hosts
from hoststools import backup_configs
from hoststools.common import list_hosts, reboot_addresses
from hoststools.upgrade import upgrade_hosts_firmware_start, upgrade_hosts_routeros_start

class Mutex(click.Option):
    def __init__(self, *args, **kwargs):
        self.not_required_if:list = kwargs.pop("not_required_if")

        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs["help"] = (kwargs.get("help", "") + "Option is mutually exclusive with " + ", ".join(self.not_required_if) + ".").strip()
        super(Mutex, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        current_opt:bool = self.name in opts
        for mutex_opt in self.not_required_if:
            if mutex_opt in opts:
                if current_opt:
                    raise click.UsageError("Illegal usage: '" + str(self.name) + "' is mutually exclusive with " + str(mutex_opt) + ".")
                else:
                    self.required = False
        return super(Mutex, self).handle_parse_result(ctx, opts, args)

def validate_commands(ctx, param, values):
    execute_command = ctx.params.get('execute_command')
    commands_file = ctx.params.get('commands_file')
    
    if (not execute_command and not commands_file):
        raise click.UsageError('You must provide either -e or -C')
    
    if (execute_command and commands_file):
        raise click.UsageError('You must provide either -e or -C, but not both.')
    
    return values

@click.group(invoke_without_command=True, context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-H', '--host')
@click.option('-e', '--execute-command', cls=Mutex, not_required_if=['commands_file'])
@click.option('-i', '--inventory-file')
@click.option('-c', '--config-file', default='settings.yaml')
@click.option('-C', '--commands-file', cls=Mutex, not_required_if=['execute_command'])
@click.pass_context
def cli(ctx, host, execute_command, inventory_file, config_file, commands_file):
    if ctx.invoked_subcommand is None:
        validate_commands(ctx, None, None)
        ctx.invoke(exec,
                   host=host,
                   execute_command=execute_command,
                   inventory_file=inventory_file,
                   config_file=config_file,
                   commands_file=commands_file)

@cli.command(help='Backup configs from hosts')
@click.option('-s', '--sensitive', is_flag=True, default=False)
@click.option('-H', '--host')
@click.option('-i', '--inventory-file')
@click.option('-c', '--config-file', default='settings.yaml')
def backup(sensitive, host, inventory_file, config_file):
    hosts = get_hosts()
    backup_configs(hosts, sensitive=sensitive)

@cli.command(help='Execute commands on hosts')
@click.option('-H', '--host')
@click.option('-e', '--execute-command', required=True, cls=Mutex, not_required_if=['commands_file'])
@click.option('-i', '--inventory-file')
@click.option('-c', '--config-file', default='settings.yaml')
@click.option('-C', '--commands-file', required=True, cls=Mutex, not_required_if=['execute_command'])
def exec(host, execute_command, inventory_file, config_file, commands_file):
    hosts = get_hosts()
    
    # Getting command from arguments or config file
    commands = get_commands()
    
    # Executing commands for each host in list
    execute_hosts_commands(hosts, commands)

@cli.command(help='Check for routers with outdated firmware')
@click.argument('min-version')
@click.argument('filtered-version', required=False)
@click.option('-o', '--output-file', required=False)
@click.option('-H', '--host')
@click.option('-i', '--inventory-file')
@click.option('-c', '--config-file', default='settings.yaml')
def outdated(min_version, filtered_version, host, inventory_file, config_file, output_file):
    hosts = get_hosts()
    outdated_hosts = get_outdated_hosts(hosts, min_version, filtered_version)
    if output_file:
        with open(output_file, 'w') as output_file:
            for host in outdated_hosts:
                output_file.write(f'{host}\n')
    else:
        list_outdated_hosts(outdated_hosts)

@cli.command(help='List routers')
@click.option('-H', '--host')
@click.option('-i', '--inventory-file')
@click.option('-c', '--config-file', default='settings.yaml')
def list(host, inventory_file, config_file):
    hosts = get_hosts()
    list_hosts(hosts)

@cli.command(help='Reboot routers')
@click.option('-H', '--host')
@click.option('-i', '--inventory-file')
@click.option('-c', '--config-file', default='settings.yaml')
def reboot(host, inventory_file, config_file):
    addresses = get_hosts()
    reboot_addresses(addresses)

@cli.command(help='Upgrade routers with outdated RouterOS')
@click.option('-H', '--host')
@click.option('-i', '--inventory-file')
@click.option('-c', '--config-file', default='settings.yaml')
def upgrade(host, inventory_file, config_file):
    hosts = get_hosts()
    upgrade_hosts_routeros_start(hosts)

@cli.command(help='Upgrade routers with outdated firmware')
@click.option('-H', '--host')
@click.option('-i', '--inventory-file')
@click.option('-c', '--config-file', default='settings.yaml')
def upgrade_firmware(host, inventory_file, config_file):
    hosts = get_hosts()
    upgrade_hosts_firmware_start(hosts)

if __name__ == '__main__':
    cli()
