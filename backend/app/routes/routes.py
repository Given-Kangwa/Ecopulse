from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Route
from app.schemas.route import RouteResponse


router = APIRouter(
    prefix="/api/routes",
    tags=["Routes"]
)


@router.get(
    "/",
    response_model=list[RouteResponse]
)
def get_routes(
    db: Session = Depends(get_db)
):
    routes = (
        db.query(Route)
        .order_by(Route.route_id)
        .all()
    )

    return routes


@router.get(
    "/{route_id}",
    response_model=RouteResponse
)
def get_route(
    route_id: int,
    db: Session = Depends(get_db)
):
    route = (
        db.query(Route)
        .filter(Route.route_id == route_id)
        .first()
    )

    if not route:
        raise HTTPException(
            status_code=404,
            detail="Route not found"
        )

    return route