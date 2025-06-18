from .file import FileInventorySource
from .netbox import NetboxInventorySource
from .single import SingleInventorySource
from .static import StaticInventorySource

__all__ = [
    'FileInventorySource',
    'NetboxInventorySource',
    'SingleInventorySource',
    'StaticInventorySource',
]
