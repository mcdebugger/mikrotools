from typing import Protocol, runtime_checkable

from .models import InventoryItem

@runtime_checkable
class InventorySource(Protocol):
    def get_hosts(self) -> list[InventoryItem]:
        ...