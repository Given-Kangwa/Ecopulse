from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional


class PaymentResponse(BaseModel):
    payment_id: int
    household_id: int
    amount: float
    payment_date: date
    payment_method: str
    transaction_reference: Optional[str] = None
    received_by: Optional[int] = None
    receipt_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)