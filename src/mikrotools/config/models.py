import yaml

from pydantic import BaseModel

class Base (BaseModel):
    pass

class Inventory(Base):
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
    inventory: Inventory = Inventory()

    @classmethod
    def from_yaml(cls, path: str) -> 'Config':
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            return cls(**data)
