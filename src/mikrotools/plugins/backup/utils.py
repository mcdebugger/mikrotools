from packaging import version
from rich.console import Console

from mikrotools.hoststools.models import MikrotikHost
from mikrotools.netapi import MikrotikManager
from mikrotools.tools.colors import fcolors_256 as fcolors

def get_device_config(host, sensitive=False):
    # Exporting current config
    with MikrotikManager.get_connection(host=host.address) as device:
        if sensitive:
            # Exporting sensitive config
            if version.parse(host.installed_routeros_version) >= version.parse('7.0'):
                # RouterOS 7.0+
                current_config = device.execute_command_raw('/export show-sensitive')
            else:
                # RouterOS < 7.0
                current_config = device.execute_command_raw('/export')
        else:
            # Exporting non-sensitive config
            if version.parse(host.installed_routeros_version) >= version.parse('7.0'):
                # RouterOS 7.0+
                current_config = device.execute_command_raw('/export')
            else:
                # RouterOS < 7.0
                current_config = device.execute_command_raw('/export hide-sensitive')
        
    return current_config

def backup_configs(addresses, sensitive=False):
    counter = 1
    failed_hosts = []
    
    for address in addresses:
        host = MikrotikHost(address=address)
        try:
            with MikrotikManager.get_connection(host=address) as device:
                host.identity = device.get_identity()
                host.installed_routeros_version = device.get_routeros_installed_version()
                
                print_backup_progress(host, counter, len(addresses), len(addresses) - counter + 1)
                
                current_config = get_device_config(host, sensitive)
        except Exception as e:
            failed_hosts.append(host)
            continue
        
        # Writing current config to file
        with open(f'{host.identity}.rsc', 'w') as f:
            f.write(current_config)
        
        counter += 1
    
    console = Console(highlight=False)
    print(f'\r\033[K', end='\r')

    if len(failed_hosts) > 0:
        console.print(f'[bold orange1]Backup completed with errors!\n'
                       f'[bold gold1]Backed up {len(addresses) - len(failed_hosts)} '
                       f'hosts out of {len(addresses)}\n')
        console.print(f'[bold red3]The following hosts failed to backup:')
        for host in failed_hosts:
            console.print(f'[thistle1]{host.address}')
    else:
        console.print(f'[bold green]All hosts backed up successfully!')

def print_backup_progress(host, counter, total, remaining):
    print(f'\r{fcolors.darkgray}Backing up {fcolors.lightblue}{host.identity} '
        f'{fcolors.blue}({fcolors.yellow}{host.address}{fcolors.blue}) '
        f'{fcolors.red}[{counter}/{total}]'
        f'{fcolors.cyan} Remaining: {fcolors.lightpurple}{remaining}{fcolors.default}'
        f'\033[K',
        end='')
