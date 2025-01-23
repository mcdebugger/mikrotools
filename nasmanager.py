#!/usr/bin/env python3

from tools.config import get_hosts
from tools.ssh import execute_hosts_commands

def main():
    hosts = get_hosts()

    # Executing commands for each host in list
    execute_hosts_commands(hosts)

if __name__ == '__main__':
    main()
