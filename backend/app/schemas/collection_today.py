from datetime import date, time
from typing import Optional

from pydantic import BaseModel


class TodayCollectionResponse(BaseModel):
    schedule_id: int
    route_id: int
    route_name: str

    scheduled_date: date
    scheduled_time: Optional[time] = None

    household_id: int
    house_number: str
    street: str

    payment_status: Optional[str] = None
    amount_outstanding: float = 0.0
    collection_preference: str

    collection_decision: str
    collection_status: Optional[str] = None