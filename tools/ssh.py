import paramiko

from tools.args import parse_args
from tools.config import get_commands_from_file, load_cfg_from_file

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
