from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Household


router = APIRouter(
    prefix="/api/households",
    tags=["Households"]
)


@router.get("/")
def get_households(db: Session = Depends(get_db)):
    households = db.query(Household).all()

    return households
@router.get("/{household_id}")
def get_household(
    household_id: int,
    db: Session = Depends(get_db)
):
    household = (
        db.query(Household)
        .filter(Household.household_id == household_id)
        .first()
    )

    if not household:
        return {
            "error": "Household not found"
        }

    return household