import asyncio

from packaging import version
from rich import print as rprint
from rich.console import Console
from rich.prompt import Confirm

from .models import MikrotikHost

from mikrotools.netapi import MikrotikManager, AsyncMikrotikManager

async def get_mikrotik_host(address: str) -> MikrotikHost:
    async with await AsyncMikrotikManager.get_connection(address) as device:
        identity = await device.get_identity()
        installed_routeros_version = await device.get_routeros_installed_version()
        latest_routeros_version = await device.get_routeros_latest_version()
        current_firmware_version = await device.get_current_firmware_version()
        upgrade_firmware_verion = await device.get_upgrade_firmware_version()
        cpu_load = int(await device.get('/system resource', 'cpu-load'))
        model = await device.get('/system routerboard', 'model')
        if version.parse(installed_routeros_version) >= version.parse('7.0'):
            uptime = await device.get('/system resource', 'uptime as-string')
        else:
            uptime = await device.get('/system resource', 'uptime')
        public_address = await device.get('/ip cloud', 'public-address')
    
    return MikrotikHost(
        address=address,
        identity=identity,
        installed_routeros_version=installed_routeros_version,
        latest_routeros_version=latest_routeros_version,
        current_firmware_version=current_firmware_version,
        upgrade_firmware_version=upgrade_firmware_verion,
        cpu_load=cpu_load,
        model=model,
        uptime=uptime,
        public_address=public_address
    )
                
def print_reboot_progress(host, counter, total, remaining):
    # Clears the current line
    print('\r\033[K', end='')
    # Prints the reboot progress
    rprint(f'[grey27]Rebooting [sky_blue2]{host.identity if host.identity is not None else "-"} '
            f'[blue]([yellow]{host.address}[blue]) '
            f'[red]\\[{counter}/{total}] '
            f'[cyan]Remaining: [medium_purple1]{remaining}',
            end=''
    )

def reboot_addresses(addresses):
    hosts = []

    print(f'The following hosts will be rebooted:')
    for address in addresses:
        rprint(f'[light_slate_blue]Host: [bold sky_blue1]{address}')
    
    is_reboot_confirmed = Confirm.ask(f'[bold yellow]Would you like to reboot devices now?[/] '
                                      f'[bold red]\\[y/n][/]', show_choices=False)

    if not is_reboot_confirmed:
        exit()
    else:
        [hosts.append(MikrotikHost(address=address)) for address in addresses]
        reboot_hosts(hosts)

def reboot_hosts(hosts):
    failed = 0
    failed_hosts = []
    counter = 1
    console = Console(highlight=False)
    
    for host in hosts:
        print_reboot_progress(host, counter, len(hosts), len(hosts) - counter + 1)
        try:
            reboot_host(host)
        except Exception as e:
            failed += 1
            failed_hosts.append(host)
        counter += 1
    
    print(f'\r\033[K', end='\r')
    print('')
    if failed > 0:
        console.print(f'[bold orange1]Rebooted {len(hosts) - failed} hosts out of {len(hosts)}!\n')
        console.print(f'[bold red3]The following hosts failed to reboot:')
        for host in failed_hosts:
            console.print(f'[grey78]{host.address}')
        exit()
    rprint(f'[bold green]All hosts rebooted successfully!')

def reboot_host(host):
    with MikrotikManager.get_connection(host.address) as device:
        device.execute_command('/system reboot')
