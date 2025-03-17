from functools import wraps
from importlib.metadata import entry_points

import click

from mikrotools.tools.log import setup_logging

class Mutex(click.Option):
    def __init__(self, *args, **kwargs):
        self.not_required_if:list = kwargs.pop("not_required_if")

        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs["help"] = (kwargs.get("help", "") + "Option is mutually exclusive with " + ", ".join(self.not_required_if) + ".").strip()
        super(Mutex, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        current_opt:bool = self.name in opts
        for mutex_opt in self.not_required_if:
            if mutex_opt in opts:
                if current_opt:
                    raise click.UsageError("Illegal usage: '" + str(self.name) + "' is mutually exclusive with " + str(mutex_opt) + ".")
                else:
                    self.required = False
        return super(Mutex, self).handle_parse_result(ctx, opts, args)

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

@click.group(invoke_without_command=True, context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-e', '--execute-command', cls=Mutex, not_required_if=['commands_file'])
@click.option('-C', '--commands-file', cls=Mutex, not_required_if=['execute_command'])
@common_options
@click.pass_context
def cli(ctx, *args, **kwargs):
    # Setting up logging
    setup_logging(ctx.params['debug'])
    
    # Invoking default command
    if ctx.invoked_subcommand is None:
        validate_commands(ctx, None, None)
        cmd = cli.get_command(ctx, 'exec')
        if not cmd:
            raise click.UsageError("Default 'exec' command not found.")
        ctx.invoke(cmd, *args, **kwargs)

def load_plugins(cli_group):
    for entry_point in entry_points(group='mikrotools.plugins'):
        try:
            plugin = entry_point.load()
            plugin.register(cli_group)
        except Exception as e:
            click.secho(
                f'Failed to load plugin {entry_point.name}: {e}',
                fg='red', err=True
            )

def validate_commands(ctx, param, values):
    execute_command = ctx.params.get('execute_command')
    commands_file = ctx.params.get('commands_file')
    
    if (not execute_command and not commands_file):
        raise click.UsageError('You must provide either -e or -C')
    
    if (execute_command and commands_file):
        raise click.UsageError('You must provide either -e or -C, but not both.')
    
    return values
