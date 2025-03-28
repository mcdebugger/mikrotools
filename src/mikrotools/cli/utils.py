from functools import wraps
from importlib.metadata import entry_points

import click

from mikrotools.cli.options import common_options
from mikrotools.tools.log import setup_logging
from mikrotools.tools import cleanup_all

class AliasedGroup(click.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aliases: dict[str, str] = {}
        
    def command(self, *args, **kwargs):
        aliases = kwargs.pop('aliases', [])
        decorator = super().command(*args, **kwargs)
        if not aliases:
            return decorator
        
        def decorator_with_aliases_wrapper(f):
            cmd = decorator(f)
            if aliases:
                for alias in aliases:
                    if alias in self.aliases:
                        raise click.ClickException(f'Alias {alias} is already taken by {self.aliases[alias]}')
                    self.aliases[alias] = cmd.name
            return cmd
        
        return decorator_with_aliases_wrapper
    
    def group(self, *args, **kwargs):
        aliases = kwargs.pop('aliases', [])
        decorator = super().group(*args, **kwargs)
        if not aliases:
            return decorator
        
        def decorator_with_aliases_wrapper(f):
            cmd = decorator(f)
            if aliases:
                for alias in aliases:
                    if alias in self.aliases:
                        raise click.ClickException(f'Alias {alias} is already taken by {self.aliases[alias]}')
                    self.aliases[alias] = cmd.name
            return cmd
        
        return decorator_with_aliases_wrapper
    
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        
        # Try to resolve alias
        if cmd_name in self.aliases:
            return click.Group.get_command(self, ctx, self.aliases[cmd_name])
        
        # Try to resolve ambiguous command
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        matches += [v for k, v in self.aliases.items() if k.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail(f'Too many matches: {", ".join(sorted(matches))}')
    
    def resolve_command(self, ctx, args):
        _, cmd, args, = super().resolve_command(ctx, args)
        return cmd.name, cmd, args        

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

@click.group(cls=AliasedGroup, context_settings=dict(help_option_names=['-h', '--help']))
@common_options
@click.pass_context
def cli(ctx, *args, **kwargs):
    # Setting up logging
    setup_logging(ctx.params['debug'])
    ctx.call_on_close(cleanup_all)
    
    # Invoking default command
    # if ctx.invoked_subcommand is None:
    #     cmd = cli.get_command(ctx, 'exec')
    #     if not cmd:
    #         raise click.UsageError("Default 'exec' command not found.")
    #     ctx.invoke(cmd, *args, **kwargs)

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
