import asyncio

from packaging import version
from rich import print as rprint
from rich.console import Console
from rich.prompt import Confirm

from mikrotools.cli.progress import Progress

from .models import MikrotikHost
from .models.operations import OperationType

from mikrotools.netapi import MikrotikManager, AsyncMikrotikManager

__all__ = [
    'cleanup_connections',
    'get_mikrotik_host',
    'reboot_addresses',
    'reboot_hosts',
    'reboot_host'
]

def cleanup_connections():
    MikrotikManager.close_all()
    asyncio.run(AsyncMikrotikManager.close_all())

async def get_mikrotik_host(address: str) -> MikrotikHost:
    async with AsyncMikrotikManager.async_session(address) as device:
        identity = await device.get_identity()
        pkgupdate = await device.get_system_package_update()
        routerboard = await device.get_system_routerboard()
        cpu_load = int(await device.get('/system resource', 'cpu-load'))
        if version.parse(pkgupdate.installed_version) >= version.parse('7.0'):
            uptime = await device.get('/system resource', 'uptime as-string')
        else:
            uptime = await device.get('/system resource', 'uptime')
        public_address = await device.get('/ip cloud', 'public-address')
    
    return MikrotikHost(
        address=address,
        identity=identity,
        installed_routeros_version=pkgupdate.installed_version,
        latest_routeros_version=pkgupdate.latest_version,
        current_firmware_version=routerboard.current_firmware,
        upgrade_firmware_version=routerboard.upgrade_firmware,
        cpu_load=cpu_load,
        model=routerboard.model,
        uptime=uptime,
        public_address=public_address
    )

async def reboot_addresses(addresses):
    print('The following hosts will be rebooted:')
    for address in addresses:
        rprint(f'[light_slate_blue]Host: [bold sky_blue1]{address}')
    
    if Confirm.ask(
        f'[bold yellow]Would you like to reboot devices now?[/] '
        f'[bold red]\\[y/n][/]',
        show_choices=False,
    ):
        hosts = []
        
        [hosts.append(MikrotikHost(address=address)) for address in addresses]
        await reboot_hosts(hosts)
    else:
        exit()

async def reboot_hosts(hosts):
    failed = 0
    failed_addresses = []
    tasks = []
    counter = 0
    console = Console(highlight=False)
    
    for host in hosts:
        task = asyncio.create_task(reboot_host(host), name=host.address)
        tasks.append(task)
    
    with Progress(OperationType.REBOOT) as progress:
        progress.update(counter=counter, total=len(hosts))
        async for task in asyncio.as_completed(tasks):
            counter += 1
            try:
                host = await task
            except TimeoutError:
                failed += 1
                failed_addresses.append((task.get_name(), 'Connection timeout'))
            except Exception as e:
                failed += 1
                failed_addresses.append((task.get_name(), str(e)))
            
            progress.update(counter=counter, total=len(hosts), host=host)
    
    console.line()
    if failed > 0:
        console.print(f'[bold orange1]Rebooted {len(hosts) - failed} hosts out of {len(hosts)}!\n')
        console.print('[bold red3]The following hosts failed to reboot:')
        for address, error in failed_addresses:
            console.print(f'[red]{address}: [yellow]{error}')
        exit()
    console.print('[bold green]All hosts rebooted successfully!')

async def reboot_host(host):
    async with AsyncMikrotikManager.async_session(host.address) as device:
        await device.execute_command_raw('/system reboot')
    
    return host
