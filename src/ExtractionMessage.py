from pydantic import BaseModel
from Params import Params


class ExtractionMessage(BaseModel):
    tenant: str
    task: str
    params: Params
    success: bool
    error_message: str = None
    file_url: str = None
