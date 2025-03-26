from dataclasses import dataclass
from enum import Enum

@dataclass
class OperationTemplate:
    name: str
    description: str | None = None
    text: str | None = None

class OperationType(Enum):
    REBOOT = OperationTemplate(name='reboot')
