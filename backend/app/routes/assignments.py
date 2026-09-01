from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import CollectionAssignment
from app.schemas.assignment import AssignmentResponse


router = APIRouter(
    prefix="/api/assignments",
    tags=["Assignments"]
)


@router.get(
    "/",
    response_model=list[AssignmentResponse]
)
def get_assignments(
    db: Session = Depends(get_db)
):
    assignments = (
        db.query(CollectionAssignment)
        .order_by(
            CollectionAssignment.assignment_date.desc(),
            CollectionAssignment.assignment_id
        )
        .all()
    )

    return assignments



@router.get(
    "/worker/{worker_id}"
)
def get_worker_assignments(
    worker_id: int,
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT
            ca.assignment_id,
            ca.worker_id,
            w.full_name AS worker_name,
            ca.route_id,
            r.route_name,
            ca.assignment_date,
            ca.status
        FROM collection_assignments ca

        JOIN workers w
            ON ca.worker_id = w.worker_id

        JOIN routes r
            ON ca.route_id = r.route_id

        WHERE ca.worker_id = :worker_id

        ORDER BY
            ca.assignment_date DESC,
            ca.assignment_id DESC;
    """)

    result = db.execute(
        query,
        {"worker_id": worker_id}
    )

    return result.mappings().all()

@router.get(
    "/{assignment_id}",
    response_model=AssignmentResponse
)
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db)
):
    assignment = (
        db.query(CollectionAssignment)
        .filter(
            CollectionAssignment.assignment_id == assignment_id
        )
        .first()
    )

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    return assignment
