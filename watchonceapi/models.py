from pydantic import BaseModel


class SecretModel(BaseModel):
    text: str
    expire_time: int = 0
