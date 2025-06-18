from mikrotools.inventory.protocol import InventorySource
from mikrotools.inventory.models import InventoryItem

class SingleInventorySource(InventorySource):
    def __init__(self, address: str):
        self.address = address
    
    def get_hosts(self) -> list[InventoryItem]:
        return [InventoryItem(address=self.address)]
