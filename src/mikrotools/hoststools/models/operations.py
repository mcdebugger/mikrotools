from dataclasses import dataclass
from enum import Enum

@dataclass
class OperationTemplate:
    name: str
    description: str | None = None
    text: str | None = None

class OperationType(Enum):
    BACKUP = OperationTemplate(name='backup')
    CHECKUPGRADABLE = OperationTemplate(name='upgradable hosts check', text='Checking for updates...')
    REBOOT = OperationTemplate(name='reboot')
    UPGRADE = OperationTemplate(name='upgrade')
