from rich import print as rprint
from rich.console import Console
from rich.prompt import Confirm

from .models import MikrotikHost

from mikrotools.netapi import MikrotikManager

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
