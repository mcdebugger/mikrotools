import asyncio

from asyncssh.misc import PermissionDenied
from ipaddress import IPv4Address
from packaging import version
from rich.box import SIMPLE
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.table import Table

from mikrotools.hoststools.common import get_mikrotik_host
from mikrotools.hoststools.models import MikrotikHost
from mikrotools.netapi import AsyncMikrotikManager

def create_table():
    table = Table(title="[green]List of hosts", show_header=True, header_style="bold grey78", box=SIMPLE)
    
    table.add_column("Host", justify="left")
    table.add_column("Address", justify="left")
    table.add_column('Public Address', justify="left")
    table.add_column("RouterOS", justify="left")
    table.add_column("Firmware", justify="left")
    table.add_column("Model", justify="left")
    table.add_column("CPU %", justify="right")
    table.add_column("Uptime", justify="left")
    
    return table

def generate_table(table, rows):
    table = create_table()
    add_rows(table, rows)
    
    return table

def add_rows(table, rows):
    for row in sorted(rows, key=IPv4Address):
        host, failed, error_message = rows[row]
        add_row(table, host, failed, error_message)

def get_footer(rows, offline_hosts):
    footer = ''
    footer += (f'[medium_purple1]{"-" * 15}\n')
    footer += (f'[cornflower_blue]Total hosts: '
                    f'[light_steel_blue1]{len(rows)} '
                    f'[medium_purple1]| '
                    f'[cornflower_blue]Online hosts: '
                    f'[green]{len(rows) - offline_hosts} '
                    f'[medium_purple1]| '
                    f'[cornflower_blue]Offline hosts: '
                    f'[red]{offline_hosts} '
                    f'\n')
    
    return footer

def print_table(rows):
    console = Console()
    table = create_table()
    
    console.clear()

    add_rows(table, rows)
    
    console.print(table)

async def list_hosts(addresses, follow: bool = False):
    hosts = []
    tasks = []
    rows = {}
    offline_hosts = 0
    
    console = Console()
    layout = Layout()
    table = create_table()
    footer = get_footer(rows=rows, offline_hosts=offline_hosts)
    layout.split_column(
        Layout(table, name='table'),
        Layout(footer, name='footer', size=3)
    )
    
    for address in addresses:
        task = asyncio.create_task(get_mikrotik_host(address), name=address)
        tasks.append(task)

    with Live(layout, console=console, screen=True, refresh_per_second=10) as live:
        async for task in asyncio.as_completed(tasks):
            error_message = None
            failed = False
            try:
                host = await task
                hosts.append(host)
            except TimeoutError:
                failed = True
                host = MikrotikHost(address=task.get_name())
                error_message = 'Connection timeout'
                offline_hosts += 1
            except PermissionDenied:
                failed = True
                host = MikrotikHost(address=task.get_name())
                error_message = 'Authentication failed'
            except TypeError as e:
                raise e
            except Exception as e:
                failed = True
                host = MikrotikHost(address=task.get_name())
                error_message = str(e)
            
            rows[task.get_name()] = (host, failed, error_message)
            
            table = generate_table(table, rows)
            footer = get_footer(rows=rows, offline_hosts=offline_hosts)
            layout['table'].update(table)
            layout['footer'].update(footer)
    
    # Print the final table
    console.clear()
    console.print(table)
    console.print(footer)

def add_row(table: Table, host: MikrotikHost, failed: bool = False, error_message: str = None):
    if host is not None:
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
