import asyncio

from datetime import datetime
from rich.console import Console

from mikrotools.inventory import InventoryItem
from mikrotools.netapi import AsyncMikrotikManager

async def execute_host_commands(host: InventoryItem, commands: list[str]) -> tuple[str, str, datetime, list[tuple[str, str]]]:
    async with AsyncMikrotikManager.async_session(host) as device:
        identity = await device.get_identity()
        routeros_installed_version = await device.get_routeros_installed_version()
        results: list[tuple[str, str]] = []
        
        for command in commands:
            result = await device.execute_command_raw(command)
            results.append((command, result),)
        
    return(
        (
            identity,
            routeros_installed_version,
            datetime.now(),
            results,
        )
    )

async def execute_hosts_commands(hosts: list[InventoryItem], commands: list[str]) -> None:
    tasks: list[asyncio.Task] = []
    
    console = Console()
    console.print('[gray27]Executing commands on hosts...')
    
    tasks.extend(
        asyncio.create_task(
            execute_host_commands(host, commands), name=host.address
        )
        for host in hosts
    )
    async for task in asyncio.as_completed(tasks):
        try:
            identity, routeros_installed_version, dt, results = await task
        except TimeoutError:
            console.print(
                f'[bold red3]Error connecting to [/]'
                f'[light_pink3]{task.get_name()}:[/] ' # type: ignore
                f'[gold3]Connection timeout[/]'
            )
            continue
        except Exception as e:
            console.print(
                f'[bold red3]Error while executing command on '
                f'[light_pink3]{task.get_name()}:[/] [gold3]{e}[/]' # type: ignore
            )
            continue
        
        # Printing separator
        console.print(f'[bold sky_blue2]{"-"*35}[/]')
        console.print(f'[bold sky_blue2]Address:[/] [medium_purple1]{task.get_name()}[/]') # type: ignore
        
        # Printing host information
        console.print(f'[bold sky_blue2]Identity:[/] [medium_purple1]{identity}[/]')
        console.print(f'[bold sky_blue2]RouterOS version:[/] [medium_purple1]{routeros_installed_version}[/]')
        
        # Printing date and time
        console.print(f'[bold sky_blue2]Executed at:[/] [medium_purple1]{dt.strftime("%Y-%m-%d %H:%M:%S")}[/]')
        
        # Printing results
        for command, result in results:
            console.line()
            # Printing command
            console.print(f'[bold grey27]Executed command: {command}[/]')
            # Printing execution result
            console.print(result)
