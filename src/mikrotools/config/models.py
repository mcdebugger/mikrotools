import yaml

from pydantic import BaseModel

class Base (BaseModel):
    pass

class InventorySourceConfig(Base):
    type: str
    path: str | None = None
    hosts: list[str] | None = None
    file: str | None = None
    url: str | None = None
    token: str | None = None
    filters: dict | None = None

class InventoryConfig(Base):
    sources: list[InventorySourceConfig] = []
    hostsFile: str | None = None

class JumpHost(Base):
    address: str | None = None
    port: int = 22
    username: str | None = None
    password: str | None = None
    keyfile: str | None = None

class SSHConfig(Base):
    port: int = 22
    username: str | None = None
    password: str | None = None
    keyfile: str | None = None
    jump: bool = False
    jumphost: JumpHost = JumpHost()

class Config(Base):
    ssh: SSHConfig = SSHConfig()
    inventory: InventoryConfig = InventoryConfig()

    @classmethod
    def from_yaml(cls, path: str) -> 'Config':
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            return cls(**data)
