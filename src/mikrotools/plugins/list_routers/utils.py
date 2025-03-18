from packaging import version
from paramiko import AuthenticationException
from rich.box import SIMPLE
from rich.console import Console
from rich.table import Table

from mikrotools.hoststools.models import MikrotikHost
from mikrotools.netapi import MikrotikManager

def list_hosts(addresses):
    offline_hosts = 0
    console = Console()
    table = Table(title="[green]List of hosts", show_header=True, header_style="bold grey78", box=SIMPLE)
    
    table.add_column("Host", justify="left")
    table.add_column("Address", justify="left")
    table.add_column('Public Address', justify="left")
    table.add_column("RouterOS", justify="left")
    table.add_column("Firmware", justify="left")
    table.add_column("Model", justify="left")
    table.add_column("CPU %", justify="right")
    table.add_column("Uptime", justify="left")
    
    console.clear()
    console.print(table)
    
    for address in addresses:
        failed = False
        error_message = None
        host = MikrotikHost(address=address)
        
        try:
            with MikrotikManager.get_connection(address) as device:
                host.identity = device.get_identity()
                host.public_address = device.get('/ip cloud', 'public-address')
                host.installed_routeros_version = device.get_routeros_installed_version()
                host.current_firmware_version = device.get('/system routerboard', 'current-firmware')
                host.model = device.get('/system routerboard', 'model')
                host.cpu_load = int(device.get('/system resource', 'cpu-load'))
                if version.parse(host.installed_routeros_version) >= version.parse('7.0'):
                    host.uptime = device.get('/system resource', 'uptime as-string')
                else:
                    host.uptime = device.get('/system resource', 'uptime')
        except TimeoutError:
            failed = True
            error_message = 'Connection timeout'
            offline_hosts += 1
        except AuthenticationException:
            failed = True
            error_message = 'Authentication failed'
        except Exception as e:
            failed = True
            error_message = str(e)
        
        if failed:
            table.add_row(
                f'[red]{host.identity if host.identity is not None else "-"}', # Host
                f'[light_steel_blue1]{host.address if host.address is not None else "-"}', # Address
                f'[red]{error_message if error_message is not None else "-"}'
            )
        else:
            if host.cpu_load is None:
                cpu_color = 'red'
            elif host.cpu_load < 40:
                cpu_color = 'green'
            elif host.cpu_load < 60:
                cpu_color = 'yellow'
            elif host.cpu_load < 80:
                cpu_color = 'dark_orange'
            else:
                cpu_color = 'red'
            
            table.add_row(
                f'[dark_orange]{host.identity if host.identity is not None else "-"}', # Host
                f'[light_steel_blue1]{host.address if host.address is not None else "-"}', # Address
                f'[slate_blue1]{host.public_address if host.public_address is not None else "-"}', # Public address
                f'[dark_olive_green3]{host.installed_routeros_version if host.installed_routeros_version is not None else "-"}', # RouterOS
                f'[medium_purple1]{host.current_firmware_version if host.current_firmware_version is not None else "-"}', # Firmware
                f'[dodger_blue2]{host.model if host.model is not None else "-"}', # Model
                f'[{cpu_color}]{host.cpu_load if host.cpu_load is not None else "-"}%', # CPU %
                f'[cornflower_blue]{host.uptime if host.uptime is not None else "-"}', # Uptime
            )
        
        console.clear()
        console.print(table)
        
        console.print(f'[medium_purple1]{"-" * 15}')
        console.print(f'[cornflower_blue]Total hosts: '
                      f'[light_steel_blue1]{len(table.rows)} '
                      f'[medium_purple1]| '
                      f'[cornflower_blue]Online hosts: '
                      f'[green]{len(table.rows) - offline_hosts} '
                      f'[medium_purple1]| '
                      f'[cornflower_blue]Offline hosts: '
                      f'[red]{offline_hosts} '
                      f'\n')
