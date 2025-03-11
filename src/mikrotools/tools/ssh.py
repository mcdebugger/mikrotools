from packaging import version

from mikrotools.netapi import MikrotikManager
from mikrotools.tools.colors import fcolors_256 as fcolors

def execute_hosts_commands(hosts, commands):
    for host in hosts:
        # Printing separator
        print(f'{fcolors.bold}{fcolors.lightblue}{"-"*30}{fcolors.default}')
        print(f'{fcolors.bold}{fcolors.lightblue}Working with host: {fcolors.lightpurple}{host}{fcolors.default}')
        
        with MikrotikManager.get_connection(host) as device:
            identity = device.get_identity()
            print(f'{fcolors.bold}{fcolors.lightblue}Identity: {fcolors.lightpurple}{identity}{fcolors.default}')
            installed_version = device.get_routeros_installed_version()
            print(f'{fcolors.bold}{fcolors.lightblue}Installed version: {fcolors.lightpurple}{installed_version}{fcolors.default}')
            
            # Executing commands
            for command in commands:
                print(f'\n{fcolors.bold}{fcolors.darkgray}Executing command: {command}{fcolors.default}')
                result = device.execute_command_raw(command)
                # Printing execution result
                print(result)

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
        print_progress(host, counter, len(hosts), len(outdated_hosts), offline)

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

def print_progress(host, counter, total, outdated, offline):
        print(f'\r{fcolors.darkgray}Checking host {fcolors.yellow}{host} '
            f'{fcolors.red}[{counter}/{total}] '
            f'{fcolors.cyan}Outdated: {fcolors.lightpurple}{outdated}{fcolors.default} '
            f'{fcolors.cyan}Offline: {fcolors.red}{offline}{fcolors.default}',
            end='')

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
