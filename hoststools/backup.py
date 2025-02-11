from tools.colors import fcolors_256 as fcolors
from tools.ssh import HostCommandsExecutor

from .models import MikrotikHost

def backup_configs(addresses):
    counter = 1
    
    for address in addresses:
        host = MikrotikHost(address=address)
        executor = HostCommandsExecutor(address)
        host.identity = executor.execute_command(':put [/system identity get name]')
        print_backup_progress(host, counter, len(addresses), len(addresses) - counter + 1)
        current_config = executor.execute_command('/export')
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
