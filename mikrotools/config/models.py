import yaml

from pydantic import BaseModel

class Base (BaseModel):
    pass

class Inventory(Base):
    hostsFile: str = None

class JumpHost(Base):
    address: str = None
    port: int = 22
    username: str = None
    password: str = None
    keyfile: str = None

class SSHConfig(Base):
    port: int = 22
    username: str = None
    password: str = None
    keyfile: str = None
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
