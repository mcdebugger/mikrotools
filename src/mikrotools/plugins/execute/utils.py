from rich.console import Console

from mikrotools.netapi import MikrotikManager, AsyncMikrotikManager

def execute_hosts_commands(hosts, commands):
    console = Console()
    console.print('[gray27]Executing commands on hosts...')
    for host in hosts:
        # Printing separator
        console.print(f'[bold sky_blue2]{"-"*30}[/]')
        console.print(f'[bold sky_blue2]Working with host:[/] [medium_purple1]{host}[/]')
        
        with MikrotikManager.session(host) as device:
            identity = device.get_identity()
            console.print(f'[bold sky_blue2]Identity:[/] [medium_purple1]{identity}[/]')
            installed_version = device.get_routeros_installed_version()
            console.print(f'[bold sky_blue2]Installed version:[/] [medium_purple1]{installed_version}[/]')
            
            # Executing commands
            for command in commands:
                console.line()
                console.print(f'[bold grey27]Executing command: {command}[/]')
                result = device.execute_command_raw(command)
                # Printing execution result
                console.print(result)
