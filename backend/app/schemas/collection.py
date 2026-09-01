from datetime import date, time, datetime
from typing import Optional

from pydantic import BaseModel


class CollectionResponse(BaseModel):
    collection_record_id: int
    schedule_id: int
    household_id: int
    status: str
    missed_reason: Optional[str] = None
    company_responsible: Optional[bool] = None
    rescheduled_date: Optional[date] = None
    notes: Optional[str] = None
    recorded_at: Optional[datetime] = None


class CollectionCreate(BaseModel):
    schedule_id: int
    household_id: int
    status: str
    missed_reason: Optional[str] = None
    company_responsible: Optional[bool] = None
    rescheduled_date: Optional[date] = None
    notes: Optional[str] = None

from datetime import date
from typing import Optional

from pydantic import BaseModel


class CollectionUpdate(BaseModel):
    status: str
    missed_reason: Optional[str] = None
    company_responsible: Optional[bool] = None
    rescheduled_date: Optional[date] = None
    notes: Optional[str] = None