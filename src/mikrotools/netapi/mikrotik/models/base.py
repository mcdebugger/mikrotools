from pydantic import BaseModel

def to_dash(string: str) -> str:
    return string.replace('_', '-')

class MikrotikBase(BaseModel):
    class Config:
        alias_generator = to_dash
