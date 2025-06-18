from mikrotools.inventory.models import InventoryItem
from mikrotools.inventory.protocol import InventorySource

class StaticInventorySource(InventorySource):
    def __init__(self, hosts: list[str]):
        self.hosts = hosts

    def get_hosts(self) -> list[InventoryItem]:
        return [InventoryItem(address=host) for host in self.hosts]