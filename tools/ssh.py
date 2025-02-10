import paramiko

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

def get_outdated_hosts(hosts, version):
    """
    Gets a list of hosts that do not have the specified or higher version installed.

    Args:
        hosts (list): A list of hostnames or IP addresses to check.
        version (str): The version to compare against.

    Returns:
        list: A list of hosts that do not have the specified version installed.
    """
    counter = 1
    outdated_hosts = []
    for host in hosts:
        print(f'{fcolors.darkgray}Checking host {fcolors.yellow}{host} {fcolors.red}[{counter}/{len(hosts)}]{fcolors.default}', end='\r')

        if not check_against_version(host, version):
            outdated_hosts.append(host)
        
        counter += 1
    
    print(' ' * 50, end='\r')
    
    return outdated_hosts

def check_against_version(host, version):
    """
    Checks if the installed version on a given host is up-to-date with the specified version.

    Args:
        host (str): The hostname or IP address of the device to check.
        version (str): The version to compare against.

    Returns:
        bool: True if the installed version is greater than or equal to the specified version, False otherwise.
    """

    executor = HostCommandsExecutor(host)
    
    installed_version = executor.execute_command(':put [/system package update get installed-version]')
    
    if installed_version >= version:
        return True
    else:
        return False