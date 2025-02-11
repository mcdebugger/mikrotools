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
        self.ssh.connect(host, username=user, key_filename=keyfile, port=port, disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']})
    
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
        print(f'{fcolors.darkgray}Checking host {fcolors.yellow}{host} '
              f'{fcolors.red}[{counter}/{len(hosts)}] ',
              f'{fcolors.cyan}Outdated: {fcolors.lightpurple}{len(outdated_hosts)}{fcolors.default} ',
              end='\r')

        if check_if_update_applicable(host, min_version, filtered_version):
            outdated_hosts.append(host)
        
        counter += 1
    
    print(' ' * 50, end='\r')
    
    return outdated_hosts

def check_if_update_applicable(host, min_version, filtered_version):
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
    executor = HostCommandsExecutor(host)
    
    installed_version = version.parse(executor.execute_command(':put [/system package update get installed-version]'))
    
    if installed_version < version.parse(min_version):
        if filtered_version:
            return installed_version >= version.parse(filtered_version)
        else:
            return True
    else:
        return False