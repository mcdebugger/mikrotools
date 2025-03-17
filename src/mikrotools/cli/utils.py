from functools import wraps

import click

def common_options(func):
    @click.option('-H', '--host', help='Target host')
    @click.option('-P', '--port', type=int, help='SSH port')
    @click.option('-u', '--user', help='Username')
    @click.option('-p', '--password', is_flag=True, help='Prompt for password')
    @click.option('-c', '--config-file')
    @click.option('-i', '--inventory-file')
    @click.option('-j', '--jump', is_flag=True, help='Use jump host')
    @click.option('-d', '--debug', is_flag=True, help='Enable debug mode')
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
