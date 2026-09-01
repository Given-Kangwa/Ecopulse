from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Payment
from app.schemas.payment import PaymentResponse


router = APIRouter(
    prefix="/api/payments",
    tags=["Payments"]
)


@router.get("/", response_model=list[PaymentResponse])
def get_payments(db: Session = Depends(get_db)):
    payments = (
        db.query(Payment)
        .order_by(Payment.payment_date.desc())
        .all()
    )

    return payments


@router.get("/household/{household_id}", response_model=list[PaymentResponse])
def get_household_payments(
    household_id: int,
    db: Session = Depends(get_db)
):
    payments = (
        db.query(Payment)
        .filter(Payment.household_id == household_id)
        .order_by(Payment.payment_date.desc())
        .all()
    )

    return payments