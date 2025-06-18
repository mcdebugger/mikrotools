from mikrotools.inventory.models import InventoryItem
from mikrotools.inventory.protocol import InventorySource


class FileInventorySource(InventorySource):
    def __init__(self, inventory_file: str):
        self.inventory_file = inventory_file

    def get_hosts(self) -> list[InventoryItem]:
        return [InventoryItem(address=address) for address in self.read_from_file()]
    
    def read_from_file(self) -> list[str]:
        try:
            with open(self.inventory_file) as f:
                return [line.strip() for line in f if not line.startswith('#')]
        except FileNotFoundError as e:
            raise FileNotFoundError(f'Inventory file not found: {self.inventory_file}') from e
