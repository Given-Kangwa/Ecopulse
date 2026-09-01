from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ComplaintResponse(BaseModel):
    complaint_id: int
    household_id: int
    resident_id: int
    category: str
    description: str
    priority: str
    status: str
    assigned_worker_id: Optional[int] = None
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None


class ComplaintCreate(BaseModel):
    household_id: int
    resident_id: int
    category: str
    description: str
    priority: str = "MEDIUM"


class ComplaintUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_worker_id: Optional[int] = None
    resolution_notes: Optional[str] = None