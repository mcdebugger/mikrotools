from packaging import version

from tools.colors import fcolors_256 as fcolors
from tools.ssh import HostCommandsExecutor

from .models import MikrotikHost

def backup_configs(addresses, sensitive=False):
    counter = 1
    
    for address in addresses:
        host = MikrotikHost(address=address)
        executor = HostCommandsExecutor(address)
        host.identity = executor.execute_command(':put [/system identity get name]')
        host.installed_routeros_version = executor.execute_command(':put [/system package update get installed-version]')
        
        print_backup_progress(host, counter, len(addresses), len(addresses) - counter + 1)
        
        # Exporting current config
        if sensitive:
            # Exporting sensitive config
            if version.parse(host.installed_routeros_version) >= version.parse('7.0'):
                # RouterOS 7.0+
                current_config = executor.execute_command('/export show-sensitive')
            else:
                # RouterOS < 7.0
                current_config = executor.execute_command('/export')
        else:
            # Exporting non-sensitive config
            if version.parse(host.installed_routeros_version) >= version.parse('7.0'):
                # RouterOS 7.0+
                current_config = executor.execute_command('/export')
            else:
                # RouterOS < 7.0
                current_config = executor.execute_command('/export hide-sensitive')
        with open(f'{host.identity}.rsc', 'w') as f:
            f.write(current_config)
        del executor
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
