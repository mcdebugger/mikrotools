from .base import Base, Host

class MikrotikHost(Host):
    identity: str | None = None
    installed_routeros_version: str | None = None
    latest_routeros_version: str | None = None
    current_firmware_version: str | None = None
    upgrade_firmware_version: str | None = None
    cpu_load: int | None = None
    model: str | None = None
    uptime: str | None = None
    public_address: str | None = None
