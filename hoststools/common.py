from tools.colors import fcolors_256 as fcolors
from tools.ssh import HostCommandsExecutor

def print_reboot_progress(host, counter, total, remaining):
        print(f'\r{fcolors.darkgray}Rebooting {fcolors.lightblue}{host["identity"]} {fcolors.blue}({fcolors.yellow}{host["host"]}{fcolors.blue}) '
            f'{fcolors.red}[{counter}/{total}] '
            f'{fcolors.cyan}Remaining: {fcolors.lightpurple}{remaining}{fcolors.default}'
            f'\033[K',
            end='')

def reboot_hosts(hosts):
    counter = 1
    for host in hosts:
        print_reboot_progress(host, counter, len(hosts), len(hosts) - counter + 1)
        reboot_host(host['host'])
        counter += 1
    
    print(f'\r\033[K', end='\r')
    print(f'{fcolors.bold}{fcolors.green}All hosts rebooted successfully!{fcolors.default}')

def reboot_host(host):
    executor = HostCommandsExecutor(host)
    executor.execute_command('/system reboot')
    del executor
