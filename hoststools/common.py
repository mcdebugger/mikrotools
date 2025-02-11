from packaging import version
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
    table.add_column("Model", justify="left")
    table.add_column("CPU %", justify="left")
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
        host.model = executor.execute_command(':put [/system routerboard get model]')
        host.cpu_load = int(executor.execute_command(':put [/system resource get cpu-load]'))
        if version.parse(host.installed_routeros_version) >= version.parse('7.0'):
            host.uptime = executor.execute_command(':put [/system resource get uptime as-string]')
        else:
            host.uptime = executor.execute_command(':put [/system resource get uptime]')
        
        del executor
        
        if host.cpu_load < 40:
            cpu_color = 'green'
        elif host.cpu_load < 60:
            cpu_color = 'yellow'
        elif host.cpu_load < 80:
            cpu_color = 'dark_orange'
        else:
            cpu_color = 'red'
        
        table.add_row(
            f'[dark_orange]{host.identity}', # Host
            f'[light_steel_blue1]{host.address}', # Address
            f'[slate_blue1]{host.public_address}', # Public address
            f'[dark_olive_green3]{host.installed_routeros_version}', # RouterOS
            f'[medium_purple1]{host.current_firmware_version}', # Firmware
            f'[dodger_blue2]{host.model}', # Model
            f'[{cpu_color}]{host.cpu_load}%', # CPU %
            f'[cornflower_blue]{host.uptime}', # Uptime
        )
        
        console.clear()
        console.print(table)

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
