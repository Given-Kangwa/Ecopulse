from pydantic import BaseModel, ConfigDict
from typing import Optional


class WorkerResponse(BaseModel):
    worker_id: int
    full_name: str
    phone_number: Optional[str] = None
    role: str
    status: str

    model_config = ConfigDict(from_attributes=True)