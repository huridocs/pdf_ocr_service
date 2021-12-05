from pydantic import BaseModel
from typing import Optional


class Params(BaseModel):
    filename: str
    language: Optional[str] = 'en'
