from rich.box import SIMPLE
from rich.console import Console
from rich.table import Table

from .models import MikrotikHost

from tools.colors import fcolors_256 as fcolors
from tools.ssh import HostCommandsExecutor

def list_hosts(addresses):
    console = Console()
    table = Table(title="[green]List of hosts", show_header=True, header_style="bold grey78", box=SIMPLE)
    
    table.add_column("Host", justify="left")
    table.add_column("Address", justify="left")
    table.add_column('Public Address', justify="left")
    table.add_column("RouterOS", justify="left")
    table.add_column("Firmware", justify="left")
    table.add_column("Uptime", justify="left")
    
    console.clear()
    console.print(table)
    
    for address in addresses:
        host = MikrotikHost(address=address)
        executor = HostCommandsExecutor(address)
        
        host.identity = executor.execute_command(':put [/system identity get name]')
        host.public_address = executor.execute_command(':put [/ip cloud get public-address]')
        host.installed_routeros_version = executor.execute_command(':put [/system package update get installed-version]')
        host.current_firmware_version = executor.execute_command(':put [/system routerboard get current-firmware]')
        host.uptime = executor.execute_command(':put [/system resource get uptime as-string]')
        
        table.add_row(
            f'[dark_orange]{host.identity}', # Host
            f'[light_steel_blue1]{host.address}', # Address
            f'[slate_blue1]{host.public_address}', # Public address
            f'[dark_olive_green3]{host.installed_routeros_version}', # RouterOS
            f'[medium_purple1]{host.current_firmware_version}', # Firmware
            f'[cornflower_blue]{host.uptime}', # Uptime
        )
        
        console.clear()
        console.print(table)
        
        del executor

def print_reboot_progress(host, counter, total, remaining):
        print(f'\r{fcolors.darkgray}Rebooting {fcolors.lightblue}{host.identity} '
              f'{fcolors.blue}({fcolors.yellow}{host.address}{fcolors.blue}) '
              f'{fcolors.red}[{counter}/{total}] '
              f'{fcolors.cyan}Remaining: {fcolors.lightpurple}{remaining}{fcolors.default}'
              f'\033[K',
              end='')

def reboot_hosts(hosts):
    counter = 1
    for host in hosts:
        print_reboot_progress(host, counter, len(hosts), len(hosts) - counter + 1)
        reboot_host(host)
        counter += 1
    
    print(f'\r\033[K', end='\r')
    print(f'{fcolors.bold}{fcolors.green}All hosts rebooted successfully!{fcolors.default}')

def reboot_host(host):
    executor = HostCommandsExecutor(host.address)
    executor.execute_command('/system reboot')
    del executor
