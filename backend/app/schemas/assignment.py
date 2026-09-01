from datetime import date
from pydantic import BaseModel


class AssignmentResponse(BaseModel):
    assignment_id: int
    worker_id: int
    route_id: int
    assignment_date: date
    status: str