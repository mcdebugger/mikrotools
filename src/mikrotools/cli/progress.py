from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner

from mikrotools.hoststools.models import MikrotikHost, OperationType

class Progress:
    def __init__(self, optype: OperationType, message: str | None = None, show_spinner: bool = True) -> None:
        self._optype = optype
        self._console = Console(highlight=False)
        self._spinner_enabled = show_spinner
        self._message: str = message if message is not None else ''
        if self._spinner_enabled:
            self._spinner = Spinner('dots', text=self._message, style='status.spinner')

        self._live = Live(self.renderable, console=self._console, refresh_per_second=10.0, transient=True)
    
    @property
    def renderable(self) -> Spinner | str:
        return self._spinner if self._spinner_enabled else self._message
    
    def __enter__(self) -> "Progress":
        self._live.start()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._live.stop()
    
    def _form_message(
        self,
        counter: int | None = None,
        total: int | None = None,
        host: MikrotikHost | None = None,
        address: str | None = None,
        identity: str | None = None,
    ) -> str:
        delimiter = f'[medium_violet_red]|[/]'
        message = f'[grey27]Performing[/] [slate_blue3]{self._optype.value.name}[/][grey27]...[/]'

        # Add counter and total
        if counter is not None and total is not None:
            message += f' [red]\\[{counter}/{total}][/]'
            remaining = total - counter
        
        # Add remaining
        if remaining is not None:
            message += f' {delimiter} [cyan]Remaining:[/] [medium_purple1]{remaining}[/]'

        if (
            identity is not None
            or address is not None
            or (
                host is not None and (
                    host.identity is not None or host.address is not None)
                )
        ):
            message += f' {delimiter} [dark_sea_green4]Recent host:[/]'
        
        # Add identity
        if identity is None:
            if host is not None and host.identity is not None:
                identity = host.identity
        if identity is not None:
            message += f' [sky_blue2]{identity}[/]'
        
        # Add address
        # If address is not provided, try touse the host address
        if address is None:
            if host is not None and host.address is not None:
                address = host.address
        # If address is set, use it
        if address is not None:
            if identity is not None:
                message += f' [blue]([/][yellow]{address}[/][blue])[/]'
            else:
                message += f' [yellow]{address}[/]'
        
        return message
    
    def _update(self, message: str) -> None:
        self._message = message
        
        if self._spinner_enabled:
            self._spinner = Spinner('dots', text=self._message, style='status.spinner')

        self._live.update(self.renderable, refresh=True)
    
    def update(
        self,
        counter: int | None = None,
        total: int | None = None,
        host: MikrotikHost | None = None,
        address: str | None = None,
        identity: str | None = None,
        message: str | None = None
    ) -> None:
        if message is None:
            message = self._form_message(counter, total, host, address, identity)
        
        self._update(message)
    