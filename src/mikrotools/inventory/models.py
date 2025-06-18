from pydantic import BaseModel


class InventoryItem(BaseModel):
    address: str
    name: str | None = None
    description: str | None = None
