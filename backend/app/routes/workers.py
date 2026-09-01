from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Worker
from app.schemas.worker import WorkerResponse


router = APIRouter(
    prefix="/api/workers",
    tags=["Workers"]
)


@router.get(
    "/",
    response_model=list[WorkerResponse]
)
def get_workers(
    db: Session = Depends(get_db)
):
    workers = (
        db.query(Worker)
        .order_by(Worker.worker_id)
        .all()
    )

    return workers


@router.get(
    "/{worker_id}",
    response_model=WorkerResponse
)
def get_worker(
    worker_id: int,
    db: Session = Depends(get_db)
):
    worker = (
        db.query(Worker)
        .filter(Worker.worker_id == worker_id)
        .first()
    )

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    return worker