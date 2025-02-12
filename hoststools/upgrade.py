from packaging import version

from .common import reboot_hosts
from .models import MikrotikHost

from tools.colors import fcolors_256 as fcolors
from tools.ssh import HostCommandsExecutor

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

def print_check_upgradable_progress(host, counter, total, outdated, offline):
        print(f'\r{fcolors.darkgray}Checking host {fcolors.lightblue}{host.identity} '
              f'{fcolors.cyan}({fcolors.yellow}{host.address}{fcolors.cyan}) '
              f'{fcolors.red}[{counter}/{total}] '
              f'{fcolors.lightpurple}| {fcolors.cyan}Upgradable: {fcolors.lightpurple}{outdated}{fcolors.default} '
              f'{fcolors.lightpurple}| {fcolors.cyan}Offline: {fcolors.red}{offline}{fcolors.default}'
              f'\033[K',
              end='')

def print_upgrade_progress(host, counter, total, remaining):
        print(f'\r{fcolors.darkgray}Upgrading {fcolors.lightblue}{host.identity} '
              f'{fcolors.blue}({fcolors.yellow}{host.address}{fcolors.blue}) '
              f'{fcolors.red}[{counter}/{total}] '
              f'{fcolors.cyan}Remaining: {fcolors.lightpurple}{remaining}{fcolors.default}'
              f'\033[K',
              end='')

def get_firmware_upgradable_hosts(addresses):
    upgradable_hosts = []
    offline = 0
    counter = 1
    
    for address in addresses:
        host = MikrotikHost(address=address)
        host.identity = '-'
        print_check_upgradable_progress(host, counter, len(addresses), len(upgradable_hosts), offline)
        
        try:
            executor = HostCommandsExecutor(address)
        except TimeoutError:
            offline += 1
            counter += 1
            continue
        else:
            host.identity = executor.execute_command(':put [/system identity get name]')
            print_check_upgradable_progress(host, counter, len(addresses), len(upgradable_hosts), offline)
            
            host.current_firmware_version = executor.execute_command(':put [/system routerboard get current-firmware]')
            host.upgrade_firmware_version = executor.execute_command(':put [/system routerboard get upgrade-firmware]')

            del executor
        
        if is_upgradable(host.current_firmware_version, host.upgrade_firmware_version):
            upgradable_hosts.append(host)
        
        counter += 1
    
    print('\r\033[K', end='\r')
    
    return upgradable_hosts

def get_routeros_upgradable_hosts(addresses) -> list[MikrotikHost]:
    upgradable_hosts = []
    offline = 0
    counter = 1
    
    for address in addresses:
        host = MikrotikHost(address=address)
        host.identity = '-'
        print_check_upgradable_progress(host, counter, len(addresses), len(upgradable_hosts), offline)
        try:
            executor = HostCommandsExecutor(address)
        except TimeoutError:
            offline += 1
            counter += 1
            continue
        else:
            host.identity = executor.execute_command(':put [/system identity get name]')
            print_check_upgradable_progress(host, counter, len(addresses), len(upgradable_hosts), offline)
            executor.execute_command('/system package update check-for-updates')
            host.installed_routeros_version = executor.execute_command(':put [/system package update get installed-version]')
            host.latest_routeros_version = executor.execute_command(':put [/system package update get latest-version]')

            del executor
        
        if is_upgradable(host.installed_routeros_version, host.latest_routeros_version):
            upgradable_hosts.append(host)
        
        counter += 1
    
    print('\r\033[K', end='\r')
    
    return upgradable_hosts

def upgrade_hosts_firmware_start(addresses):
    """
    Starts the process of upgrading the firmware of the given hosts.

    This function checks which hosts have outdated firmware and prompts the user to
    confirm whether they want to upgrade them.

    Args:
        addresses (list[str]): A list of IP addresses or hostnames to check.
    """
    upgradable_hosts = get_firmware_upgradable_hosts(addresses)
    upgrade_hosts_firmware_confirmation_prompt(upgradable_hosts)

def upgrade_hosts_firmware_confirmation_prompt(upgradable_hosts):
    """
    Prompts the user to confirm whether they want to upgrade the specified hosts.

    Prints the list of hosts that will be upgraded and their respective
    identities. Then prompts the user to answer with 'y' to proceed with the
    upgrade or 'n' to exit the program.

    Args:
        upgradable_hosts (list[MikrotikHost]): A list of dictionaries each containing the
            information of a host to be upgraded.
    """
    # Checks if there are any hosts to upgrade
    if len(upgradable_hosts) == 0:
        print(f'{fcolors.bold}{fcolors.green}No hosts to upgrade firmware{fcolors.default}')
        exit()
    
    # Prints the list of hosts that will be upgraded
    print(f'{fcolors.bold}{fcolors.yellow}Upgradable hosts: {fcolors.red}{len(upgradable_hosts)}{fcolors.default}')
    print(f'\nThe following list of devices will be upgraded:\n')
    
    for host in upgradable_hosts:
        print(f'{fcolors.lightblue}Host: {fcolors.bold}{fcolors.green}{host.identity}'
              f'{fcolors.default} ({fcolors.lightpurple}{host.address}{fcolors.default})'
              f' {fcolors.blue}[{fcolors.red}{host.current_firmware_version} > {fcolors.green}{host.upgrade_firmware_version}{fcolors.blue}]'
              f'{fcolors.default}')

    # Prompts the user if they want to proceed
    print(f'\n{fcolors.bold}{fcolors.yellow}Are you sure you want to proceed? {fcolors.red}[y/N]{fcolors.default}')
    answer = input()
    
    # Continues or exits the program
    if answer.lower() == 'y':
        upgrade_hosts_firmware_apply(upgradable_hosts)
    else:
        exit()

def upgrade_hosts_firmware_apply(hosts):
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

    counter = 1
    for host in hosts:
        print_upgrade_progress(host, counter, len(hosts), len(hosts) - counter + 1)
        upgrade_host_firmware(host)
        counter += 1
    
    print(f'\r\033[K', end='\r')
    print(f'{fcolors.bold}{fcolors.green}All hosts upgraded successfully!{fcolors.default}')
    print(f'{fcolors.bold}{fcolors.yellow}Would you like to reboot devices now? {fcolors.red}[y/n]{fcolors.default}')
    while True:
        answer = input()
        if answer.lower() == 'y':
            reboot_hosts(hosts)
            break
        elif answer.lower() == 'n':
            exit()
        else:
            print(f'{fcolors.bold}{fcolors.yellow}Invalid input. Please enter "y" or "n".{fcolors.default}')

def upgrade_host_firmware(host):
    """
    Upgrades the firmware of the specified host.

    :param host: A MikrotikHost object representing the host to upgrade.
    :return: None
    """
    executor = HostCommandsExecutor(host.address)
    executor.execute_command('/system routerboard upgrade')
    del executor

def upgrade_hosts_routeros_start(addresses: list[str]) -> None:
    """
    Starts the process of upgrading RouterOS on the given hosts.

    This function checks which hosts have outdated RouterOS and prompts the user to
    confirm whether they want to upgrade them.

    Args:
        addresses (list[str]): A list of IP addresses or hostnames to check.
    """
    upgradable_hosts = get_routeros_upgradable_hosts(addresses)
    upgrade_hosts_routeros_confirmation_prompt(upgradable_hosts)

def upgrade_hosts_routeros_confirmation_prompt(upgradable_hosts: list[MikrotikHost]) -> None:
    # Checks if there are any hosts to upgrade
    """
    Prompts the user to confirm whether they want to upgrade the specified hosts.

    Prints the list of hosts that will be upgraded and their respective
    identities. Then prompts the user to answer with 'y' to proceed with the
    upgrade or 'n' to exit the program.

    Args:
        upgradable_hosts (list[MikrotikHost]): A list of objects each containing the
            information of a host to be upgraded.
    """
    if len(upgradable_hosts) == 0:
        print(f'{fcolors.bold}{fcolors.green}No hosts to upgrade firmware{fcolors.default}')
        exit()
    
    # Prints the list of hosts that will be upgraded
    print(f'{fcolors.bold}{fcolors.yellow}Upgradable hosts: {fcolors.red}{len(upgradable_hosts)}{fcolors.default}')
    print(f'\nThe following list of devices will be upgraded:\n')
    
    for host in upgradable_hosts:
        print(f'{fcolors.lightblue}Host: {fcolors.bold}{fcolors.green}{host.identity}'
              f'{fcolors.default} ({fcolors.lightpurple}{host.address}{fcolors.default}) '
              f'{fcolors.blue}[{fcolors.red}{host.installed_routeros_version} > {fcolors.green}{host.latest_routeros_version}{fcolors.blue}]'
              f'{fcolors.default}')

    print(f'\n{fcolors.bold}{fcolors.yellow}Are you sure you want to proceed? {fcolors.red}[y/N]{fcolors.default}')
    answer = input()
    
    if answer.lower() == 'y':
        upgrade_hosts_routeros_apply(upgradable_hosts)
    else:
        exit()

def upgrade_hosts_routeros_apply(hosts: list[MikrotikHost]) -> None:
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
    counter = 1
    for host in hosts:
        print_upgrade_progress(host, counter, len(hosts), len(hosts) - counter + 1)
        upgrade_host_routeros(host)
        counter += 1
    
    print(f'\r\033[K', end='\r')
    print(f'{fcolors.bold}{fcolors.green}All hosts upgraded successfully!{fcolors.default}')

def upgrade_host_routeros(host: MikrotikHost) -> None:
    """
    Upgrades the RouterOS version on the specified host.

    This function connects to the given host using SSH and initiates the RouterOS
    package update installation.

    Args:
        host (MikrotikHost): A MikrotikHost object representing the host to upgrade.
                             The host's address is used to establish the connection.

    Returns:
        None
    """

    executor = HostCommandsExecutor(host.address)
    executor.execute_command('/system package update install')
    del executor
