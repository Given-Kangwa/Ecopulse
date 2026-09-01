from pydantic import BaseModel
from datetime import date


class BillingStatusResponse(BaseModel):
    billing_id: int
    household_id: int
    house_number: str
    street: str
    billing_period: date
    amount_due: float
    amount_paid: float
    amount_outstanding: float
    payment_status: str
    due_date: date