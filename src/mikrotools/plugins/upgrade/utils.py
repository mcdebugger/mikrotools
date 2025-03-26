import asyncio
import logging

from enum import Enum, auto
from packaging import version
from rich.console import Console
from rich import print as rprint

from mikrotools.hoststools.common import get_mikrotik_host, reboot_hosts
from mikrotools.hoststools.models import MikrotikHost

from mikrotools.netapi import MikrotikManager, AsyncMikrotikManager
from mikrotools.tools.colors import fcolors_256 as fcolors

logger = logging.getLogger(__name__)

class UpgradeType(Enum):
    ROUTEROS = 'RouterOS'
    FIRMWARE = 'firmware'

def capfirst(s: str) -> str:
    return s[:1].upper() + s[1:]

def is_upgradable(current_version, upgrade_version):
    """
    Checks if the given `current_version` is upgradable to `upgrade_version`.

    Args:
        current_version (str): The current version of the host.
        upgrade_version (str): The version to check against.

    Returns:
        bool: True if the version is upgradable, False otherwise.
    """
    if current_version and upgrade_version:
        return version.parse(current_version) < version.parse(upgrade_version)

def print_check_upgradable_progress(counter, total, outdated, offline, failed=0, address: str = None, identity: str = None):
    console = Console()
    
    if offline > 0:
        offline_color = 'red'
    else:
        offline_color = 'green'
    
    if failed > 0:
        failed_color = 'red'
    else:
        failed_color = 'green'
    
    print('\r\033[K', end='\r')
    console.print(f'[grey27]Checked hosts: '
                  f'[red]\\[{counter}/{total}] '
                  f'[medium_purple1]| [cyan]Upgradable: [medium_purple1]{outdated} '
                  f'[medium_purple1]| [cyan]Offline: [{offline_color}]{offline} '
                  f'[medium_purple1]| [cyan]Errors: [{failed_color}]{failed}'
                  f'{" [medium_purple1]| [cyan]Last checked:" if identity is not None or address is not None else ""}'
                  f'{f" [sky_blue2]{identity}" if identity is not None else ""}'
                  f'{f" [cyan]([yellow]{address}[cyan])" if address is not None else ""}',
                  end=''
                  )

def print_upgrade_progress(host, counter, total, remaining):
        print(f'\r{fcolors.darkgray}Upgrading {fcolors.lightblue}{host.identity} '
              f'{fcolors.blue}({fcolors.yellow}{host.address}{fcolors.blue}) '
              f'{fcolors.red}[{counter}/{total}] '
              f'{fcolors.cyan}Remaining: {fcolors.lightpurple}{remaining}{fcolors.default}'
              f'\033[K',
              end='')

def print_outdated_progress(host, counter, total, outdated, offline):
        print(f'\r{fcolors.darkgray}Checking host {fcolors.yellow}{host} '
            f'{fcolors.red}[{counter}/{total}] '
            f'{fcolors.cyan}Outdated: {fcolors.lightpurple}{outdated}{fcolors.default} '
            f'{fcolors.cyan}Offline: {fcolors.red}{offline}{fcolors.default}',
            end='')

def print_upgradable_hosts(upgradable_hosts: list[MikrotikHost], upgrade_type: UpgradeType, addresses_with_error: list[tuple[str, str]] | None = None, subject: str = None):
    console = Console(highlight=False)
    
    if isinstance(upgrade_type, UpgradeType) and subject is None:
        subject = upgrade_type.value
    
    if addresses_with_error is not None and len(addresses_with_error) > 0:
        console.print(f'[orange1]The following hosts failed to check for '
                      f'{f"{subject} " if subject is not None else ""}updates:\n')
        for address, error in addresses_with_error:
            console.print(f'[light_slate_blue]Host: [bold sky_blue1]{address} [red]{error}')
        console.line()
    
    if len(upgradable_hosts) == 0:
        console.print(f'[bold green]No hosts to upgrade{f" {subject}" if subject is not None else ""}.')
        exit()
    
    # Prints the list of hosts that will be upgraded
    console.print(f'[bold yellow]Upgradable hosts: [red]{len(upgradable_hosts)}')
    console.line()
    console.print(
        f'{f"{capfirst(subject)} on the" if subject is not None else "The"}'
        f' following list of devices will be upgraded:\n'
    )
    
    for host in upgradable_hosts:
        if upgrade_type == UpgradeType.ROUTEROS:
            current_version = host.installed_routeros_version
            new_version = host.latest_routeros_version
        elif upgrade_type == UpgradeType.FIRMWARE:
            current_version = host.current_firmware_version
            new_version = host.upgrade_firmware_version
        
        console.print(
            f'[sky_blue2]Host: [/][bold green]{host.identity}[/]'
            f' ([medium_purple1]{host.address}[/]) '
            f'[blue]\\[[red]{current_version} [hot_pink]> [green]{new_version}[blue]]'
        )

# Upgrade firmware

async def get_host_if_firmware_upgradable(address) -> MikrotikHost:
    async with await AsyncMikrotikManager.get_connection(address) as device:
        routerboard = await device.get_system_routerboard()
        
        if is_upgradable(routerboard.current_firmware, routerboard.upgrade_firmware):
            return await get_mikrotik_host(address)
        else:
            return None

async def get_firmware_upgradable_hosts(addresses):
    upgradable_hosts = []
    tasks = []
    addresses_with_error = []
    failed = 0
    offline = 0
    counter = 0
    
    console = Console()
    
    console.show_cursor(False)
    console.print(f'[grey27]Checking for hosts applicable for firmware upgrade...')
    print_check_upgradable_progress(counter, len(addresses), len(upgradable_hosts), offline, failed)

    for address in addresses:
        task = asyncio.create_task(get_host_if_firmware_upgradable(address), name=address)
        tasks.append(task)
    
    async for task in asyncio.as_completed(tasks):
        counter += 1
        try:
            host = await task
        except TimeoutError:
            offline += 1
            addresses_with_error.append((task.get_name(), 'Connection timeout'))
            continue
        except Exception as e:
            addresses_with_error.append((task.get_name(), e))
            failed += 1
            continue
        
        if host is not None:
            upgradable_hosts.append(host)
            print_check_upgradable_progress(counter, len(addresses), len(upgradable_hosts), offline, failed, address=task.get_name(), identity=host.identity)
        else:
            print_check_upgradable_progress(counter, len(addresses), len(upgradable_hosts), offline, failed, address=task.get_name())
    
    print('\r\033[K', end='\r')
    console.show_cursor()
    
    return upgradable_hosts, addresses_with_error

async def upgrade_hosts_firmware_start(addresses):
    """
    Starts the process of upgrading the firmware of the given hosts.

    This function checks which hosts have outdated firmware and prompts the user to
    confirm whether they want to upgrade them.

    Args:
        addresses (list[str]): A list of IP addresses or hostnames to check.
    """
    upgradable_hosts, addresses_with_error = await get_firmware_upgradable_hosts(addresses)
    await upgrade_hosts_firmware_confirmation_prompt(upgradable_hosts, addresses_with_error)

async def upgrade_hosts_firmware_confirmation_prompt(upgradable_hosts, addresses_with_error):
    """
    Prompts the user to confirm whether they want to upgrade the specified hosts.

    Prints the list of hosts that will be upgraded and their respective
    identities. Then prompts the user to answer with 'y' to proceed with the
    upgrade or 'n' to exit the program.

    Args:
        upgradable_hosts (list[MikrotikHost]): A list of dictionaries each containing the
            information of a host to be upgraded.
    """

    print_upgradable_hosts(upgradable_hosts, UpgradeType.FIRMWARE, addresses_with_error=addresses_with_error)

    # Prompts the user if they want to proceed
    print(f'\n{fcolors.bold}{fcolors.yellow}Are you sure you want to proceed? {fcolors.red}[y/N]{fcolors.default}')
    answer = input()
    
    # Continues or exits the program
    if answer.lower() == 'y':
        await upgrade_hosts_firmware_apply(upgradable_hosts)
    else:
        exit()

async def upgrade_hosts_firmware_apply(hosts):
    """
    Applies the firmware upgrade to all specified hosts and provides an option
    to reboot them afterward.

    For each host in the list, this function prints the upgrade progress, upgrades
    the host's firmware, and then offers the user the choice to reboot the devices.

    Args:
        hosts (list[MikrotikHost]): A list of MikrotikHost objects representing
            the hosts to be upgraded.

    Returns:
        None
    """
    tasks = []
    failed_addresses = []
    counter = 0
    failed = 0
    
    console = Console(highlight=False)
    console.show_cursor(False)
    console.print(f'[grey27]Upgrading firmware on hosts...')
    
    for host in hosts:
        task = asyncio.create_task(upgrade_host_firmware(host))
        tasks.append(task)
    
    async for task in asyncio.as_completed(tasks):
        counter += 1
        try:
            host = await task
        except Exception as e:
            failed += 1
            failed_addresses.append((task.get_name(), e))
            continue
        
        print_upgrade_progress(host, counter, len(hosts), len(hosts) - counter)
    
    print(f'\r\033[K', end='\r')
    console.show_cursor()
    
    if failed == 0:
        console.print(f'[bold green]All hosts upgraded successfully!')
    else:
        console.print(f'[bold yellow]Upgraded {len(hosts) - failed} hosts out of {len(hosts)}!')
        console.print(f'[orange1]Some hosts failed to upgrade with errors:')
        console.line()
        for address, error in failed_addresses:
            console.print(f'[light_slate_blue]Host: [bold sky_blue1]{address} [red]{error}')
    
    console.print(f'[bold yellow]Would you like to reboot devices now? [red]\\[y/n]')
    while True:
        answer = input()
        if answer.lower() == 'y':
            await reboot_hosts(hosts)
            break
        elif answer.lower() == 'n':
            exit()
        else:
            console.print(f'[bold yellow]Invalid input. Please enter "y" or "n".')

async def upgrade_host_firmware(host):
    """
    Upgrades the firmware of the specified host.

    :param host: A MikrotikHost object representing the host to upgrade.
    :return: None
    """
    async with await AsyncMikrotikManager.get_connection(host.address) as device:
        await device.execute_command_raw('/system routerboard upgrade')

    return host

# Upgrade RouterOS

async def get_host_if_routeros_upgradable(address) -> MikrotikHost:
    async with await AsyncMikrotikManager.get_connection(address) as device:
        await device.execute_command_raw('/system package update check-for-updates')
        pkgupdate = await device.get_system_package_update()
        
        if is_upgradable(pkgupdate.installed_version, pkgupdate.latest_version):
            return await get_mikrotik_host(address)
        else:
            return None

async def get_routeros_upgradable_hosts(addresses) -> list[MikrotikHost]:
    tasks = []
    upgradable_hosts = []
    addresses_with_error = []
    failed = 0
    offline = 0
    counter = 0
    
    console = Console()
    
    console.show_cursor(False)
    console.print(f'[grey27]Checking for hosts applicable for RouterOS upgrade...')
    print_check_upgradable_progress(counter, len(addresses), len(upgradable_hosts), offline, failed)
    
    for address in addresses:
        task = asyncio.create_task(get_host_if_routeros_upgradable(address), name=address)
        tasks.append(task)
    
    async for task in asyncio.as_completed(tasks):
        counter += 1
        try:
            host = await task
        except TimeoutError:
            offline += 1
            addresses_with_error.append((task.get_name(), 'Connection timeout'))
            continue
        except Exception as e:
            addresses_with_error.append((task.get_name(), e))
            failed += 1
            continue
        
        if host is not None:
            upgradable_hosts.append(host)
            print_check_upgradable_progress(counter, len(addresses), len(upgradable_hosts), offline, failed, address=task.get_name(), identity=host.identity)
        else:
            print_check_upgradable_progress(counter, len(addresses), len(upgradable_hosts), offline, failed, address=task.get_name())
    
    print('\r\033[K', end='\r')
    console.show_cursor()
    
    logger.debug(f'get_routeros_upgradable_hosts: Upgradable hosts: {upgradable_hosts}')
    
    return upgradable_hosts, addresses_with_error

async def upgrade_hosts_routeros_start(addresses: list[str]) -> None:
    """
    Starts the process of upgrading RouterOS on the given hosts.

    This function checks which hosts have outdated RouterOS and prompts the user to
    confirm whether they want to upgrade them.

    Args:
        addresses (list[str]): A list of IP addresses or hostnames to check.
    """
    upgradable_hosts, addresses_with_error = await get_routeros_upgradable_hosts(addresses)
    await upgrade_hosts_routeros_confirmation_prompt(upgradable_hosts, addresses_with_error)

async def upgrade_hosts_routeros_confirmation_prompt(upgradable_hosts: list[MikrotikHost], addresses_with_error: list[tuple[str, str]]) -> None:
    """
    Prompts the user to confirm whether they want to upgrade the specified hosts.

    Prints the list of hosts that will be upgraded and their respective
    identities. Then prompts the user to answer with 'y' to proceed with the
    upgrade or 'n' to exit the program.

    Args:
        upgradable_hosts (list[MikrotikHost]): A list of objects each containing the
            information of a host to be upgraded.
    """
    console = Console(highlight=False)
    
    print_upgradable_hosts(upgradable_hosts, UpgradeType.ROUTEROS, addresses_with_error=addresses_with_error)
    
    answer = console.input(f'\n[bold yellow]Are you sure you want to proceed? [red]\\[y/N]')
    
    if answer.lower() == 'y':
        await upgrade_hosts_routeros_apply(upgradable_hosts)
    else:
        exit()

async def upgrade_hosts_routeros_apply(hosts: list[MikrotikHost]) -> None:
    """
    Upgrades RouterOS version on all specified hosts.

    For each host in the list, this function prints the upgrade progress, upgrades
    the host's RouterOS version, and then prints a success message.

    Args:
        hosts (list[MikrotikHost]): A list of MikrotikHost objects representing
            the hosts to be upgraded.

    Returns:
        None
    """
    tasks = []
    counter = 0
    failed = 0
    
    console = Console(highlight=False)
    console.show_cursor(False)
    
    for host in hosts:
        task = asyncio.create_task(upgrade_host_routeros(host))
        tasks.append(task)
    
    async for task in asyncio.as_completed(tasks):
        counter += 1
        try:
            host = await task
        except Exception as e:
            failed += 1
            console.print(f'[bold red]Failed to upgrade host: [light_slate_blue]{host.address}: [red]{e}')
            continue
        
        print_upgrade_progress(host, counter, len(hosts), len(hosts) - counter)
    
    print(f'\r\033[K', end='\r')
    
    if failed == 0:
        console.print(f'[bold green]All hosts upgraded successfully!')
    else:
        console.print(f'[bold yellow]Upgraded {len(hosts) - failed} hosts out of {len(hosts)}!\n')
        console.print(f'[bold red]Failed to upgrade {failed} hosts out of {len(hosts)}!')
    
    console.show_cursor()

async def upgrade_host_routeros(host: MikrotikHost) -> MikrotikHost:
    """
    Upgrades the RouterOS version on the specified host.

    This function connects to the given host using SSH and initiates the RouterOS
    package update installation.

    Args:
        host (MikrotikHost): A MikrotikHost object representing the host to upgrade.
                             The host's address is used to establish the connection.

    Returns:
        MikrotikHost: The updated MikrotikHost object.
    """
    async with await AsyncMikrotikManager.get_connection(host.address) as device:
        await device.execute_command_raw('/system package update check-for-updates')
        await device.execute_command_raw('/system package update install')
    
    return host

def get_outdated_hosts(hosts, min_version, filtered_version):

    """
    Checks the installed version of each host in the given list against the minimum
    version specified and returns a list of hosts with outdated versions.

    Args:
        hosts (list[str]): A list of hostnames or IP addresses to check.
        min_version (str): The minimum version required.
        filtered_version (str, optional): An optional version that further filters
                                          the hosts. If specified, the installed
                                          version must be greater than or equal
                                          to this version.

    Returns:
        list[str]: A list of hostnames or IP addresses with outdated versions.
    """
    counter = 1
    offline = 0
    outdated_hosts = []
    for host in hosts:
        print_outdated_progress(host, counter, len(hosts), len(outdated_hosts), offline)

        try:
            with MikrotikManager.get_connection(host) as device:
                installed_version = device.get_routeros_installed_version()
        except TimeoutError:
            offline += 1
            counter += 1
            continue
        
        if check_if_update_applicable(installed_version, min_version, filtered_version):
            outdated_hosts.append(host)
        
        counter += 1
    
    print('\r\033[K', end='\r')
    
    return outdated_hosts

def check_if_update_applicable(installed_version, min_version, filtered_version=None):
    """
    Checks the installed version of a host against the minimum version specified
    and returns True if an update is applicable, False otherwise.

    Args:
        host (str): The hostname or IP address of the host to check.
        min_version (str): The minimum version required.
        filtered_version (str, optional): An optional version that further filters
                                          the host. If specified, the installed
                                          version must be greater than or equal
                                          to this version.

    Returns:
        bool: True if an update is applicable, False otherwise.
    """
    
    installed_version = version.parse(installed_version)
    
    if installed_version < version.parse(min_version):
        if filtered_version:
            return installed_version >= version.parse(filtered_version)
        else:
            return True
    else:
        return False

def list_outdated_hosts(hosts):
    for host in hosts:
        print(f'{host}')
