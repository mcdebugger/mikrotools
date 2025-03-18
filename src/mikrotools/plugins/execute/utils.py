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
