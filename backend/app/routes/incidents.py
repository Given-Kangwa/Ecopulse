from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import (
    Incident,
    IncidentComplaint,
    Complaint,
    Route,
    Worker,
)
from app.schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
)


router = APIRouter(
    prefix="/api/incidents",
    tags=["Incidents"],
)


# ============================================================
# GET ALL INCIDENTS
# ============================================================

@router.get(
    "/",
    response_model=list[IncidentResponse],
)
def get_incidents(
    db: Session = Depends(get_db),
):
    incidents = (
        db.query(Incident)
        .order_by(Incident.created_at.desc())
        .all()
    )

    return incidents


# ============================================================
# GET COMPLAINTS LINKED TO AN INCIDENT
# IMPORTANT: Keep this BEFORE /{incident_id}
# ============================================================

@router.get(
    "/{incident_id}/complaints",
)
def get_incident_complaints(
    incident_id: int,
    db: Session = Depends(get_db),
):
    # Check that the incident exists
    incident = (
        db.query(Incident)
        .filter(
            Incident.incident_id == incident_id
        )
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    complaints = (
        db.query(Complaint)
        .join(
            IncidentComplaint,
            IncidentComplaint.complaint_id
            == Complaint.complaint_id,
        )
        .filter(
            IncidentComplaint.incident_id
            == incident_id,
        )
        .all()
    )

    return complaints


# ============================================================
# LINK A COMPLAINT TO AN INCIDENT
# ============================================================

@router.post(
    "/{incident_id}/complaints/{complaint_id}",
    status_code=201,
)
def link_complaint_to_incident(
    incident_id: int,
    complaint_id: int,
    db: Session = Depends(get_db),
):
    # Check that the incident exists
    incident = (
        db.query(Incident)
        .filter(
            Incident.incident_id == incident_id
        )
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    # Check that the complaint exists
    complaint = (
        db.query(Complaint)
        .filter(
            Complaint.complaint_id == complaint_id
        )
        .first()
    )

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found",
        )

    # Prevent duplicate links
    existing_link = (
        db.query(IncidentComplaint)
        .filter(
            IncidentComplaint.incident_id == incident_id,
            IncidentComplaint.complaint_id == complaint_id,
        )
        .first()
    )

    if existing_link:
        raise HTTPException(
            status_code=409,
            detail="Complaint is already linked to this incident",
        )

    link = IncidentComplaint(
        incident_id=incident_id,
        complaint_id=complaint_id,
        linked_at=datetime.now(timezone.utc),
    )

    db.add(link)
    db.commit()

    return {
        "message": "Complaint linked to incident",
        "incident_id": incident_id,
        "complaint_id": complaint_id,
    }


# ============================================================
# GET ONE INCIDENT
# IMPORTANT: Keep this AFTER the specific routes above
# ============================================================

@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = (
        db.query(Incident)
        .filter(
            Incident.incident_id == incident_id
        )
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return incident


# ============================================================
# CREATE INCIDENT
# ============================================================

@router.post(
    "/",
    response_model=IncidentResponse,
    status_code=201,
)
def create_incident(
    incident_data: IncidentCreate,
    db: Session = Depends(get_db),
):
    # If a route was supplied, make sure it exists
    if incident_data.route_id is not None:
        route = (
            db.query(Route)
            .filter(
                Route.route_id == incident_data.route_id
            )
            .first()
        )

        if not route:
            raise HTTPException(
                status_code=404,
                detail="Route not found",
            )

    incident = Incident(
        route_id=incident_data.route_id,
        incident_type=incident_data.incident_type,
        description=incident_data.description,
        status="OPEN",
        created_at=datetime.now(timezone.utc),
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return incident


# ============================================================
# UPDATE INCIDENT
# ============================================================

@router.patch(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def update_incident(
    incident_id: int,
    incident_data: IncidentUpdate,
    db: Session = Depends(get_db),
):
    incident = (
        db.query(Incident)
        .filter(
            Incident.incident_id == incident_id
        )
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    allowed_statuses = {
        "OPEN",
        "INVESTIGATING",
        "RESOLVED",
        "CLOSED",
    }

    # Validate status
    if (
        incident_data.status is not None
        and incident_data.status not in allowed_statuses
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid incident status",
        )

    # Update status
    if incident_data.status is not None:
        incident.status = incident_data.status

    # Update description
    if incident_data.description is not None:
        incident.description = incident_data.description

    # Validate confirming worker
    if incident_data.confirmed_by is not None:
        worker = (
            db.query(Worker)
            .filter(
                Worker.worker_id
                == incident_data.confirmed_by
            )
            .first()
        )

        if not worker:
            raise HTTPException(
                status_code=404,
                detail="Confirming worker not found",
            )

        incident.confirmed_by = incident_data.confirmed_by

    # Automatically manage resolved_at
    if incident.status in {
        "RESOLVED",
        "CLOSED",
    }:
        if incident.resolved_at is None:
            incident.resolved_at = datetime.now(timezone.utc)

    else:
        incident.resolved_at = None

    db.commit()
    db.refresh(incident)

    return incident