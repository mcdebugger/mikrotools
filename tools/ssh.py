import paramiko

from tools.colors import fcolors_256 as fcolors
from tools.config import get_commands, load_cfg_from_file

class HostCommandsExecutor():
    def __init__(self, host):
        self.ssh = None
        self.command = None
        
        # Loading configuration from file
        cfg = load_cfg_from_file('settings.yml')
        
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
        self.ssh.close()

def execute_hosts_commands(hosts):
    # Getting command from arguments or config file
    commands = get_commands()

    for host in hosts:
        # Printing separator
        print(f'{fcolors.bold}{fcolors.lightblue}{"-"*30}{fcolors.default}')
        print(f'{fcolors.bold}{fcolors.lightblue}Working with host: {fcolors.lightpurple}{host}{fcolors.default}')
        
        executor = HostCommandsExecutor(host)
        
        identity = executor.execute_command(':put [/system identity get name]')
        print(f'{fcolors.bold}{fcolors.lightblue}Identity: {fcolors.lightpurple}{identity}{fcolors.default}')
        
        # Executing commands
        for command in commands:
            print(f'\n{fcolors.bold}{fcolors.darkgray}Executing command: {command}{fcolors.default}')
            result = executor.execute_command(command)
            # Printing execution result
            print(result)
        
        # Deleting executor
        del executor
