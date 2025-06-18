import asyncio

from packaging import version
from rich.console import Console

from mikrotools.cli.progress import Progress
from mikrotools.hoststools.models import MikrotikHost, OperationType
from mikrotools.inventory import InventoryItem
from mikrotools.netapi import AsyncMikrotikManager

async def get_device_config(item: InventoryItem, sensitive: bool = False) -> tuple[MikrotikHost, str]:
    # Exporting current config
    async with AsyncMikrotikManager.async_session(item) as device:
        identity = await device.get_identity()
        installed_version = await device.get_routeros_installed_version()
        if sensitive:
            # Exporting sensitive config
            if version.parse(installed_version) >= version.parse('7.0'):
                # RouterOS 7.0+
                current_config = await device.execute_command_raw('/export show-sensitive')
            else:
                # RouterOS < 7.0
                current_config = await device.execute_command_raw('/export')
        else:
            # Exporting non-sensitive config
            if version.parse(installed_version) >= version.parse('7.0'):
                # RouterOS 7.0+
                current_config = await device.execute_command_raw('/export')
            else:
                # RouterOS < 7.0
                current_config = await device.execute_command_raw('/export hide-sensitive')
        
    host = MikrotikHost(address=item.address, identity=identity, installed_routeros_version=installed_version)
        
    return (host, current_config)

async def backup_configs(items: list[InventoryItem], sensitive=False):
    counter: int = 0
    failed_hosts: list[tuple[str, str]] = []
    tasks: list[asyncio.Task] = []
    
    for item in items:
        task = asyncio.create_task(get_device_config(item, sensitive), name=item.address)
        tasks.append(task)
    
    with Progress(OperationType.BACKUP) as progress:
        progress.update(counter, len(items))
        async for task in asyncio.as_completed(tasks):
            counter += 1
            try:
                host, current_config = await task
            except TimeoutError:
                failed_hosts.append((task.get_name(), 'Connection timeout'),)
                progress.update(counter, len(items), address=task.get_name())
                continue
            except Exception as e:
                failed_hosts.append((task.get_name(), str(e)),)
                progress.update(counter, len(items), address=task.get_name())
                continue
            
            # Writing current config to file
            with open(f'{host.identity}.rsc', 'w') as f:
                f.write(current_config)
            
            if host is not None:
                progress.update(counter, len(items), host=host)
            else:
                progress.update(counter, len(items), address=task.get_name())
    
    console = Console(highlight=False)
    
    if failed_hosts:
        console.print(f'[bold orange1]Backup completed with errors!\n'
                       f'[bold gold1]Backed up {len(items) - len(failed_hosts)} '
                       f'hosts out of {len(items)}\n')
        console.print('[bold red3]The following hosts failed to backup:')
        for address, error in failed_hosts:
            console.print(f'[thistle1]{address}: [yellow]{error}')
    else:
        console.print('[bold green]All hosts backed up successfully!')
