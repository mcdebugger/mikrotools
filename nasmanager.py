#!/usr/bin/env python3
import argparse
import paramiko
import yaml

def execute_hosts_commands(hosts):
    args = parse_args()

    # Loading configuration from file
    cfg = load_cfg_from_file('settings.yml')
    
    # Setting variables from configuration file
    user = cfg['User']
    port = cfg['Port']
    keyfile = cfg['KeyFile']

    # Getting command from arguments or config file
    if args.commands_file:
        commands = get_commands_from_file(args.commands_file)
    elif args.command:
        commands = [args.command]
    else:
        commands = [cfg['Command']]

    for host in hosts:
        print(f'Working with host: {host}')
        
        # Setting up SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)        
        # Connecting to host
        ssh.connect(host, username=user, key_filename=keyfile, port=port, disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']})
        
        # Executing commands
        for command in commands:
            stdin, stdout, stderr = ssh.exec_command(command)
            # Printing execution result
            print(stdout.read().decode())

        # Closing SSH connection
        ssh.close()

def get_commands_from_file(filename):
    with open(filename) as commands_file:
        commands = [command.rstrip() for command in commands_file]
        return commands
        
def get_hosts_from_file(filename):
    with open(filename) as hostsfile:
        hosts = [host.rstrip() for host in hostsfile]
        return hosts

def load_cfg_from_file(filename):
    with open(filename) as cfgfile:
        cfg = yaml.safe_load(cfgfile)
        return cfg

def parse_args():
    parser = argparse.ArgumentParser(description='Simple NAS/GW managing script')
    parser.add_argument('-c', '--command')
    parser.add_argument('-cf', '--commands-file')
    parser.add_argument('-H', '--host')
    parser.add_argument('-hf', '--hosts-file')
    args = parser.parse_args()
    return args
    
def main():
    # Parsing arguments provided on script execution
    args = parse_args()

    if args.host:
        hosts = [args.host]
    elif args.hosts_file:
        hosts = get_hosts_from_file(args.hosts_file)
    else:
        # Getting config from YAML file
        cfg = load_cfg_from_file('settings.yml')
        hostsfile = cfg['HostsFile']
        hosts = get_hosts_from_file(hostsfile)

    # Executing commands for each host in list
    execute_hosts_commands(hosts)

if __name__ == '__main__':
    main()
