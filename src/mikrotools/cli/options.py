import click

from functools import wraps

from click_option_group import optgroup

def common_options(func):
    @optgroup.group('SSH connection options')
    @optgroup.option('-H', '--host', help='Target host')
    @optgroup.option('-P', '--port', type=int, help='SSH port')
    @optgroup.option('-u', '--user', help='Username')
    @optgroup.option('-p', '--password', is_flag=True, help='Prompt for password')
    @optgroup.option('-j', '--jump', is_flag=True, help='Use jump host')
    @optgroup.option('-i', '--inventory-file', type=click.Path(exists=True), help='Inventory or hosts file')
    @optgroup.group('Configuration options')
    @optgroup.option('-c', '--config-file', type=click.Path(exists=True), help='Config file')
    @optgroup.option('-d', '--debug', is_flag=True, help='Enable debug mode')
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
