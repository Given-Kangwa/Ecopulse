from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class IncidentResponse(BaseModel):
    incident_id: int
    route_id: Optional[int] = None
    incident_type: str
    description: str
    status: str
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    confirmed_by: Optional[int] = None


class IncidentCreate(BaseModel):
    route_id: Optional[int] = None
    incident_type: str
    description: str


class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    description: Optional[str] = None
    confirmed_by: Optional[int] = None