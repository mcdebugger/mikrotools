#!/usr/bin/env python3

import click
import logging

from functools import wraps

from mikrotools.cli.utils import cli, load_plugins
from .config import load_config
from .netapi import MikrotikManager

def mikromanager_init(f):
    @wraps(f)
    def wrapper(port, user, password, config_file, inventory_file, jump, *args, **kwargs):
        logger = logging.getLogger(__name__)
        try:
            config = load_config(config_file)
        except Exception as e:
            logger.error(f'Failed to load config file: {e}')
            exit(1)
    
        if port is not None:
            config.ssh.port = int(port)
        if user is not None:
            config.ssh.username = user
        if password:
            config.ssh.keyfile = None
            # Password prompt
            config.ssh.password = click.prompt('Password', hide_input=True)
        if inventory_file is not None:
            config.inventory.hostsFile = inventory_file
        if jump:
            config.ssh.jump = True
        
        logger.debug(f'Config after applying command line options: {config}')
        
        # Configuring MikrotikManager
        MikrotikManager.configure(config)
        
        return f(*args, **kwargs)
    
    return wrapper

def main():
    load_plugins(cli)
    cli()

if __name__ == '__main__':
    main()
