import pynetbox

from mikrotools.inventory.models import InventoryItem
from mikrotools.inventory.protocol import InventorySource


class NetboxInventorySource(InventorySource):
    def __init__(self, api_url: str, token: str, filters: dict | None = None):
        self.api_url = api_url
        self.token = token
        self.filters = filters
    
    def get_client(self) -> pynetbox.api:
        return pynetbox.api(url=self.api_url, token=self.token)
    
    def get_hosts(self) -> list[InventoryItem]:
        nb = self.get_client()
        hosts: list[InventoryItem] = []

        if self.filters is not None:
            hosts.extend(
                InventoryItem(address=device.primary_ip4.address.split("/")[0])
                for device in nb.dcim.devices.filter(**self.filters)
            )
        else:
            hosts.extend(
                InventoryItem(address=device.primary_ip4.address.split("/")[0])
                for device in nb.dcim.devices.all()
            )
        
        return hosts
