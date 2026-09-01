from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.billing import BillingStatusResponse


router = APIRouter(
    prefix="/api/billing",
    tags=["Billing"]
)


@router.get(
    "/household/{household_id}",
    response_model=list[BillingStatusResponse]
)
def get_household_billing(
    household_id: int,
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT
            billing_id,
            household_id,
            house_number,
            street,
            billing_period,
            amount_due,
            amount_paid,
            amount_outstanding,
            payment_status,
            due_date
        FROM household_payment_status
        WHERE household_id = :household_id
        ORDER BY billing_period DESC
    """)

    result = db.execute(
        query,
        {"household_id": household_id}
    )

    return result.mappings().all()