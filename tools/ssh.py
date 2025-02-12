import paramiko

from packaging import version

from tools.colors import fcolors_256 as fcolors
from tools.config import get_config

class HostCommandsExecutor():
    def __init__(self, host):
        self.ssh = None
        self.command = None
        
        # Loading configuration from file
        cfg = get_config()
        
        # Setting variables from configuration file
        user = cfg['User']
        port = cfg['Port']
        keyfile = cfg['KeyFile']
    
        # Setting up SSH connection
        self.__setup_connection(host, user, keyfile, port)

    def __del__(self):
        # Closing SSH connection
        self.__close_connection()
    
    def execute_command(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        
        return stdout.read().decode().strip()
    
    def __setup_connection(self, host, user, keyfile, port):
        # Setting up SSH client
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        
        # Connecting to host
        self.ssh.connect(host, username=user, key_filename=keyfile, port=port,
                         disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']},
                         timeout=5)
    
    def __close_connection(self):
        # Closing SSH connection
        if self.ssh:
            self.ssh.close()

def execute_hosts_commands(hosts, commands):
    # Getting command from arguments or config file
    # commands = get_commands()

    for host in hosts:
        # Printing separator
        print(f'{fcolors.bold}{fcolors.lightblue}{"-"*30}{fcolors.default}')
        print(f'{fcolors.bold}{fcolors.lightblue}Working with host: {fcolors.lightpurple}{host}{fcolors.default}')
        
        executor = HostCommandsExecutor(host)
        
        identity = executor.execute_command(':put [/system identity get name]')
        print(f'{fcolors.bold}{fcolors.lightblue}Identity: {fcolors.lightpurple}{identity}{fcolors.default}')
        installed_version = executor.execute_command(':put [/system package update get installed-version]')
        print(f'{fcolors.bold}{fcolors.lightblue}Installed version: {fcolors.lightpurple}{installed_version}{fcolors.default}')
        
        # Executing commands
        for command in commands:
            print(f'\n{fcolors.bold}{fcolors.darkgray}Executing command: {command}{fcolors.default}')
            result = executor.execute_command(command)
            # Printing execution result
            print(result)
        
        # Deleting executor
        del executor

def get_installed_version(host):
    executor = HostCommandsExecutor(host)
    installed_version = executor.execute_command(':put [/system package update get installed-version]')
    del executor
    
    return installed_version

def get_latest_version(host):
    executor = HostCommandsExecutor(host)
    latest_version = executor.execute_command(':put [/system package update get latest-version]')
    del executor
    
    return latest_version

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
    outdated_hosts = []
    for host in hosts:
        print_progress(host, counter, len(hosts), len(outdated_hosts))

        installed_version = get_installed_version(host)
        
        if check_if_update_applicable(installed_version, min_version, filtered_version):
            outdated_hosts.append(host)
        
        counter += 1
    
    print(' ' * 50, end='\r')
    
    return outdated_hosts

def print_progress(host, counter, total, outdated):
        print(f'{fcolors.darkgray}Checking host {fcolors.yellow}{host} '
            f'{fcolors.red}[{counter}/{total}] ',
            f'{fcolors.cyan}Outdated: {fcolors.lightpurple}{outdated}{fcolors.default} ',
            end='\r')

def print_upgrade_progress(host, counter, total, remaining):
        print(f'\r{fcolors.darkgray}Upgrading {fcolors.lightblue}{host["identity"]} {fcolors.blue}({fcolors.yellow}{host["host"]}{fcolors.blue}) '
            f'{fcolors.red}[{counter}/{total}] '
            f'{fcolors.cyan}Remaining: {fcolors.lightpurple}{remaining}{fcolors.default}'
            f'{(" " * 10)}',
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

def get_upgradable_hosts(hosts):
    upgradable_hosts = []
    counter = 1
    
    for host in hosts:
        print_progress(host, counter, len(hosts), len(upgradable_hosts))
        try:
            executor = HostCommandsExecutor(host)
        except TimeoutError:
            continue
        else:
            executor.execute_command('/system package update check-for-updates')
            installed_version = executor.execute_command(':put [/system package update get installed-version]')
            latest_version = executor.execute_command(':put [/system package update get latest-version]')
            identity = executor.execute_command(':put [/system identity get name]')
            del executor
        
        if installed_version and latest_version:
            if check_if_update_applicable(installed_version, latest_version):
                upgradable_hosts.append({
                    'host': host,
                    'identity': identity,
                    'installed_version': installed_version,
                    'latest_version': latest_version
                })
        
        counter += 1
    
    print(' ' * 50, end='\r')
    
    return upgradable_hosts

def upgrade_hosts_prompt(upgradable_hosts):
    """
    Prompts the user to confirm whether they want to upgrade the specified hosts.

    Prints the list of hosts that will be upgraded and their respective
    identities. Then prompts the user to answer with 'y' to proceed with the
    upgrade or 'n' to exit the program.

    Args:
        upgradable_hosts (list): A list of dictionaries each containing the
            information of a host to be upgraded.
    """
    print(f'{fcolors.bold}{fcolors.yellow}Upgradable hosts: {fcolors.red}{len(upgradable_hosts)}{fcolors.default}')
    print(f'\nThe following list of devices will be upgraded:\n')
    
    for host in upgradable_hosts:
        print(f'{fcolors.lightblue}Host: {fcolors.bold}{fcolors.green}{host["identity"]}'
              f'{fcolors.default} ({fcolors.lightpurple}{host["host"]}{fcolors.default})'
              f' {fcolors.blue}[{fcolors.red}{host["installed_version"]} > {fcolors.green}{host["latest_version"]}{fcolors.blue}]'
              f'{fcolors.default}')

    print(f'\n{fcolors.bold}{fcolors.yellow}Are you sure you want to proceed? {fcolors.red}[y/N]{fcolors.default}')
    answer = input()
    
    if answer.lower() == 'y':
        upgrade_hosts_apply(upgradable_hosts)
    else:
        exit()

def upgrade_hosts_apply(upgradable_hosts):
    """
    Upgrades all hosts in the given list.

    :param upgradable_hosts: A list of dictionaries with information about the hosts
                             that are upgradable. Each dictionary must contain the
                             following keys:
                             - host: The hostname or IP address of the host.
                             - identity: The identity of the host (e.g. its name).
                             - installed_version: The current installed version of
                                                  the host.
                             - latest_version: The latest available version of the
                                                host.
    :return: None
    """
    counter = 1
    for host in upgradable_hosts:
        print_upgrade_progress(host, counter, len(upgradable_hosts), len(upgradable_hosts) - counter + 1)
        upgrade_host_routeros(host['host'])
        counter += 1
    
    print(f'\r{(" " * 50)}')
    print(f'{fcolors.bold}{fcolors.green}All hosts upgraded successfully!{fcolors.default}')
    
def upgrade_host_routeros(host):
    """
    Upgrades RouterOS version on the given host.

    :param host: the IP address or hostname of the host to upgrade
    :return: None
    """
    executor = HostCommandsExecutor(host)
    executor.execute_command('/system package update install')
    del executor
