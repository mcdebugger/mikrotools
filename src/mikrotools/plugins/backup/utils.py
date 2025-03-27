from packaging import version
from rich.console import Console

from mikrotools.cli.progress import Progress
from mikrotools.hoststools.models import MikrotikHost, OperationType
from mikrotools.netapi import MikrotikManager

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
    counter = 0
    failed_hosts = []
    
    with Progress(OperationType.BACKUP) as progress:
        progress.update(counter, len(addresses))
        for address in addresses:
            host = MikrotikHost(address=address)
            try:
                with MikrotikManager.get_connection(host=address) as device:
                    host.identity = device.get_identity()
                    host.installed_routeros_version = device.get_routeros_installed_version()
                    
                    current_config = get_device_config(host, sensitive)
            except Exception as e:
                failed_hosts.append(host)
                progress.update(counter, len(addresses), address=address)
                continue
        
            # Writing current config to file
            with open(f'{host.identity}.rsc', 'w') as f:
                f.write(current_config)
            
            counter += 1
            
            if host is not None:
                progress.update(counter, len(addresses), host=host)
            else:
                progress.update(counter, len(addresses), address=address)
    
    console = Console(highlight=False)

    if len(failed_hosts) > 0:
        console.print(f'[bold orange1]Backup completed with errors!\n'
                       f'[bold gold1]Backed up {len(addresses) - len(failed_hosts)} '
                       f'hosts out of {len(addresses)}\n')
        console.print(f'[bold red3]The following hosts failed to backup:')
        for host in failed_hosts:
            console.print(f'[thistle1]{host.address}')
    else:
        console.print(f'[bold green]All hosts backed up successfully!')
