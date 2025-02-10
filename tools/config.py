import yaml

from tools.args import parse_args

def get_commands():
    # Parsing arguments provided on script execution
    args = parse_args()

    if args.execute_command:
        commands = [args.execute_command]
    elif args.commands_file:
        commands = get_commands_from_file(args.commands_file)
    else:
        # Getting config from YAML file
        cfg = get_config()
        commands = [cfg['Command']]
    
    return commands

def get_commands_from_file(filename):
    with open(filename) as commands_file:
        commands = [command.rstrip() for command in commands_file]
        return commands

def get_config():
    args = parse_args()
    
    if args.config_file:
        filename = args.config_file
    else:
        filename = 'settings.yaml'
    
    # Getting config from YAML file
    cfg = load_cfg_from_file(filename)
    
    return cfg

def get_hosts():
    # Parsing arguments provided on script execution
    args = parse_args()

    if args.host:
        hosts = [args.host]
    elif args.inventory_file:
        hosts = read_hosts_from_file(args.inventory_file)
    else:
        # Getting config from YAML file
        cfg = get_config()
        hostsfile = cfg['HostsFile']
        hosts = read_hosts_from_file(hostsfile)
    
    return hosts

def read_hosts_from_file(filename):
    with open(filename) as hostsfile:
        hosts = [host.rstrip() for host in hostsfile]
        return hosts

def load_cfg_from_file(filename):
    with open(filename) as cfgfile:
        cfg = yaml.safe_load(cfgfile)
        return cfg
