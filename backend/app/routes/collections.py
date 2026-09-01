from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.connection import get_db
from app.database.models import CollectionRecord
from app.schemas.collection import (
    CollectionCreate,
    CollectionResponse,
    CollectionUpdate
)
from app.schemas.collection_today import TodayCollectionResponse


router = APIRouter(
    prefix="/api/collections",
    tags=["Collections"]
)


# ============================================================
# GET ALL COLLECTION RECORDS
# ============================================================

@router.get(
    "/",
    response_model=list[CollectionResponse]
)
def get_collections(
    db: Session = Depends(get_db)
):
    collections = (
        db.query(CollectionRecord)
        .order_by(
            CollectionRecord.recorded_at.desc()
        )
        .all()
    )

    return collections


# ============================================================
# GET TODAY'S COLLECTIONS FOR A WORKER
# IMPORTANT: This must come BEFORE /{collection_id}
# ============================================================

@router.get(
    "/today",
    response_model=list[TodayCollectionResponse]
)
def get_today_collections(
    worker_id: int,
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT
            cs.schedule_id,
            cs.route_id,
            r.route_name,
            cs.scheduled_date,
            cs.scheduled_time,

            h.household_id,
            h.house_number,
            h.street,

            hps.payment_status,
            COALESCE(hps.amount_outstanding, 0) AS amount_outstanding,

            h.collection_preference,

            hce.collection_decision,

            cr.status AS collection_status

        FROM collection_schedules cs

        JOIN collection_assignments ca
            ON cs.assignment_id = ca.assignment_id

        JOIN routes r
            ON cs.route_id = r.route_id

        JOIN households h
            ON h.route_id = cs.route_id

        LEFT JOIN household_payment_status hps
            ON h.household_id = hps.household_id
            AND hps.billing_period = (
                SELECT MAX(billing_period)
                FROM billing_records br2
                WHERE br2.household_id = h.household_id
            )

        JOIN household_collection_eligibility hce
            ON h.household_id = hce.household_id

        LEFT JOIN collection_records cr
            ON cr.schedule_id = cs.schedule_id
            AND cr.household_id = h.household_id

        WHERE ca.worker_id = :worker_id
          AND cs.scheduled_date = CURRENT_DATE

        ORDER BY
            r.route_name,
            h.household_id;
    """)

    result = db.execute(
        query,
        {"worker_id": worker_id}
    )

    return result.mappings().all()


# ============================================================
# GET ONE COLLECTION RECORD
# ============================================================

@router.get(
    "/{collection_id}",
    response_model=CollectionResponse
)
def get_collection(
    collection_id: int,
    db: Session = Depends(get_db)
):
    collection = (
        db.query(CollectionRecord)
        .filter(
            CollectionRecord.collection_record_id
            == collection_id
        )
        .first()
    )

    if not collection:
        raise HTTPException(
            status_code=404,
            detail="Collection record not found"
        )

    return collection

@router.patch(
    "/{collection_id}",
    response_model=CollectionResponse
)
def update_collection(
    collection_id: int,
    collection_data: CollectionUpdate,
    db: Session = Depends(get_db)
):
    collection = (
        db.query(CollectionRecord)
        .filter(
            CollectionRecord.collection_record_id
            == collection_id
        )
        .first()
    )

    if not collection:
        raise HTTPException(
            status_code=404,
            detail="Collection record not found"
        )

    # Validate status
    if collection_data.status not in {"COLLECTED", "MISSED"}:
        raise HTTPException(
            status_code=400,
            detail="Status must be COLLECTED or MISSED"
        )

    # MISSED requires a reason
    if (
        collection_data.status == "MISSED"
        and not collection_data.missed_reason
    ):
        raise HTTPException(
            status_code=400,
            detail="Missed collection requires a reason"
        )

    # Company-responsible missed collection must have a reschedule date
    if (
        collection_data.status == "MISSED"
        and collection_data.company_responsible is True
        and not collection_data.rescheduled_date
    ):
        raise HTTPException(
            status_code=400,
            detail="Company-responsible missed collection requires a rescheduled date"
        )

    # Update fields
    collection.status = collection_data.status
    collection.missed_reason = collection_data.missed_reason
    collection.company_responsible = collection_data.company_responsible
    collection.rescheduled_date = collection_data.rescheduled_date
    collection.notes = collection_data.notes

    db.commit()
    db.refresh(collection)

    return collection
# ============================================================
# CREATE COLLECTION RECORD
# ============================================================

@router.post(
    "/",
    response_model=CollectionResponse,
    status_code=201
)
def create_collection(
    collection_data: CollectionCreate,
    db: Session = Depends(get_db)
):
    collection = CollectionRecord(
        schedule_id=collection_data.schedule_id,
        household_id=collection_data.household_id,
        status=collection_data.status,
        missed_reason=collection_data.missed_reason,
        company_responsible=collection_data.company_responsible,
        rescheduled_date=collection_data.rescheduled_date,
        notes=collection_data.notes
    )

    db.add(collection)
    db.commit()
    db.refresh(collection)

    return collection