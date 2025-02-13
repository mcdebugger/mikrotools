from packaging import version

from netapi import MikrotikSSHClient
from tools.config import get_config
from tools.colors import fcolors_256 as fcolors

from .models import MikrotikHost

def backup_configs(addresses, sensitive=False):
    cfg = get_config()
    counter = 1
    
    for address in addresses:
        host = MikrotikHost(address=address)
        with MikrotikSSHClient(
                host=address, username=cfg['User'],
                keyfile=cfg['KeyFile'], port=cfg['Port']
            ) as device:
            host.identity = device.get_identity()
            host.installed_routeros_version = device.get_routeros_installed_version()
            
            print_backup_progress(host, counter, len(addresses), len(addresses) - counter + 1)
            
            # Exporting current config
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
            
        # Writing current config to file
        with open(f'{host.identity}.rsc', 'w') as f:
            f.write(current_config)
        
        counter += 1
    
    print(f'\r{(" " * 80)}', end='\r')
    print(f'{fcolors.bold}{fcolors.green}All hosts backed up successfully!{fcolors.default}')

def print_backup_progress(host, counter, total, remaining):
    print(f'\r{fcolors.darkgray}Backing up {fcolors.lightblue}{host.identity} '
        f'{fcolors.blue}({fcolors.yellow}{host.address}{fcolors.blue}) '
        f'{fcolors.red}[{counter}/{total}]'
        f'{fcolors.cyan} Remaining: {fcolors.lightpurple}{remaining}{fcolors.default}'
        f'{(" " * 10)}',
        end='')
