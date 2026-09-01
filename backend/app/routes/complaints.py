from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Complaint, Household, Resident
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintUpdate
)


router = APIRouter(
    prefix="/api/complaints",
    tags=["Complaints"]
)


@router.get(
    "/",
    response_model=list[ComplaintResponse]
)
def get_complaints(
    db: Session = Depends(get_db)
):
    complaints = (
        db.query(Complaint)
        .order_by(Complaint.created_at.desc())
        .all()
    )

    return complaints


@router.get(
    "/household/{household_id}",
    response_model=list[ComplaintResponse]
)
def get_household_complaints(
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

    complaints = (
        db.query(Complaint)
        .filter(Complaint.household_id == household_id)
        .order_by(Complaint.created_at.desc())
        .all()
    )

    return complaints


@router.get(
    "/{complaint_id}",
    response_model=ComplaintResponse
)
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db)
):
    complaint = (
        db.query(Complaint)
        .filter(Complaint.complaint_id == complaint_id)
        .first()
    )

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    return complaint


@router.post(
    "/",
    response_model=ComplaintResponse,
    status_code=201
)
def create_complaint(
    complaint_data: ComplaintCreate,
    db: Session = Depends(get_db)
):
    household = (
        db.query(Household)
        .filter(
            Household.household_id
            == complaint_data.household_id
        )
        .first()
    )

    if not household:
        raise HTTPException(
            status_code=404,
            detail="Household not found"
        )

    resident = (
        db.query(Resident)
        .filter(
            Resident.resident_id
            == complaint_data.resident_id
        )
        .first()
    )

    if not resident:
        raise HTTPException(
            status_code=404,
            detail="Resident not found"
        )

    if resident.household_id != complaint_data.household_id:
        raise HTTPException(
            status_code=400,
            detail="Resident does not belong to this household"
        )

    allowed_priorities = {
        "LOW",
        "MEDIUM",
        "HIGH",
        "URGENT"
    }

    if complaint_data.priority not in allowed_priorities:
        raise HTTPException(
            status_code=400,
            detail="Invalid complaint priority"
        )

    complaint = Complaint(
        household_id=complaint_data.household_id,
        resident_id=complaint_data.resident_id,
        category=complaint_data.category,
        description=complaint_data.description,
        priority=complaint_data.priority,
        status="NEW",
        created_at=datetime.now(timezone.utc)
    )

    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    return complaint


@router.patch(
    "/{complaint_id}",
    response_model=ComplaintResponse
)
def update_complaint(
    complaint_id: int,
    complaint_data: ComplaintUpdate,
    db: Session = Depends(get_db)
):
    complaint = (
        db.query(Complaint)
        .filter(Complaint.complaint_id == complaint_id)
        .first()
    )

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    allowed_statuses = {
        "NEW",
        "ASSIGNED",
        "IN_PROGRESS",
        "RESOLVED",
        "CLOSED"
    }

    allowed_priorities = {
        "LOW",
        "MEDIUM",
        "HIGH",
        "URGENT"
    }

    if (
        complaint_data.status is not None
        and complaint_data.status not in allowed_statuses
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid complaint status"
        )

    if (
        complaint_data.priority is not None
        and complaint_data.priority not in allowed_priorities
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid complaint priority"
        )

    if complaint_data.status is not None:
        complaint.status = complaint_data.status

    if complaint_data.priority is not None:
        complaint.priority = complaint_data.priority

    if complaint_data.assigned_worker_id is not None:
        complaint.assigned_worker_id = (
            complaint_data.assigned_worker_id
        )

    if complaint_data.resolution_notes is not None:
        complaint.resolution_notes = (
            complaint_data.resolution_notes
        )

    if complaint.status in {"RESOLVED", "CLOSED"}:
        if complaint.resolved_at is None:
            complaint.resolved_at = datetime.now(timezone.utc)

    elif complaint.status in {
        "NEW",
        "ASSIGNED",
        "IN_PROGRESS"
    }:
        complaint.resolved_at = None

    db.commit()
    db.refresh(complaint)

    return complaint