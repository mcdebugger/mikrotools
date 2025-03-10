from pydantic import BaseModel

class Base(BaseModel):
    pass

class Host(Base):
    address: str
    port: int | None = None
    username: str | None = None
    password: str | None = None
    keyfile: str | None = None
