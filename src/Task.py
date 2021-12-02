from pydantic import BaseModel
from Params import Params


class Task(BaseModel):
    tenant: str
    task: str
    params: Params
