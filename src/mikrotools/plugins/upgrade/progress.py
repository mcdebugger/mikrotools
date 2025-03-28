from mikrotools.cli.progress import Progress
from mikrotools.hoststools.models import OperationType

from .types import UpgradeType

class CheckUpgradableProgress(Progress):
    def __init__(self, upgrade_type: UpgradeType) -> None:
        super().__init__(OperationType.CHECKUPGRADABLE)
        self._upgrade_type = upgrade_type
    
    def _form_message(self, counter: int, total: int, outdated: int, offline: int, failed: int = 0, address: str = None, identity: str = None) -> str:
        if offline > 0:
            offline_color = 'red'
        else:
            offline_color = 'green'
        
        if failed > 0:
            failed_color = 'red'
        else:
            failed_color = 'green'
        
        message = (
            f'[grey27]Checked hosts: '
            f'[red]\\[{counter}/{total}] '
            f'[medium_purple1]| [cyan]Upgradable: [medium_purple1]{outdated} '
            f'[medium_purple1]| [cyan]Offline: [{offline_color}]{offline} '
            f'[medium_purple1]| [cyan]Errors: [{failed_color}]{failed}'
            f'{" [medium_purple1]| [cyan]Last checked:" if identity is not None or address is not None else ""}'
            f'{f" [sky_blue2]{identity}" if identity is not None else ""}'
            f'{f" [cyan]([yellow]{address}[cyan])" if address is not None else ""}'
        )
        
        return message

    def update(self, counter: int, total: int, outdated: int, offline: int, failed: int = 0, address: str = None, identity: str = None) -> None:
        message = self._form_message(counter, total, outdated, offline, failed, address, identity)
        self._update(message)
