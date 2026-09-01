from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.household import HouseholdResponse
from app.database.models import Household, Resident
from app.schemas.residents import ResidentResponse

router = APIRouter(
    prefix="/api/households",
    tags=["Households"]
)


@router.get("/", response_model=list[HouseholdResponse])
def get_households(db: Session = Depends(get_db)):
    households = db.query(Household).all()

    return households


@router.get("/{household_id}", response_model=HouseholdResponse)
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
        raise HTTPException(
            status_code=404,
            detail="Household not found"
        )

    return household

@router.get(
    "/{household_id}/residents",
    response_model=list[ResidentResponse]
)
def get_household_residents(
    household_id: int,
    db: Session = Depends(get_db)
):
    household = (
        db.query(Household)
        .filter(Household.household_id == household_id)
        .first()
    )

    if not household:
        raise HTTPException(
            status_code=404,
            detail="Household not found"
        )

    residents = (
        db.query(Resident)
        .filter(Resident.household_id == household_id)
        .all()
    )

    return residents