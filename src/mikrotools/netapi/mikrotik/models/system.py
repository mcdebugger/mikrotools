from .base import MikrotikBase

class SystemPackageUpdate(MikrotikBase):
    channel: str
    installed_version: str
    latest_version: str | None = None
    status: str | None = None

class SystemRouterboard(MikrotikBase):
    board_name: str | None = None
    current_firmware: str
    factory_firmware: str
    firmware_type: str
    model: str
    routerboard: bool
    serial_number: str
    upgrade_firmware: str

__all__ = [
    'SystemPackageUpdate',
    'SystemRouterboard'
]
