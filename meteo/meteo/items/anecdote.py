from pydantic import BaseModel


class Anecdote(BaseModel):
    text: str
