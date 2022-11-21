from pydantic import BaseModel


class WisePhrase(BaseModel):
    text: str
