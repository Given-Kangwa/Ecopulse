from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.dashboard import DashboardSummaryResponse
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    RoutePerformanceResponse,
    WorkerPerformanceResponse,
)

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse
)
def get_dashboard_summary(
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT
            -- HOUSEHOLDS
            (
                SELECT COUNT(*)
                FROM households
            ) AS total_households,

            (
                SELECT COUNT(*)
                FROM households
                WHERE service_status = 'ACTIVE'
            ) AS active_households,


            -- BILLING / PAYMENTS
            (
                SELECT COALESCE(SUM(amount_due), 0)
                FROM billing_records
            ) AS total_billed,

            (
                SELECT COALESCE(SUM(amount_allocated), 0)
                FROM payment_allocations
            ) AS total_paid,

            (
                SELECT
                    COALESCE(SUM(amount_due), 0)
                    -
                    COALESCE(
                        (
                            SELECT SUM(amount_allocated)
                            FROM payment_allocations
                        ),
                        0
                    )
                FROM billing_records
            ) AS total_outstanding,


            -- COLLECTIONS
            (
                SELECT COUNT(*)
                FROM collection_records
            ) AS total_collections,

            (
                SELECT COUNT(*)
                FROM collection_records
                WHERE status = 'COLLECTED'
            ) AS collected_collections,

            (
                SELECT COUNT(*)
                FROM collection_records
                WHERE status = 'MISSED'
            ) AS missed_collections,

            (
                SELECT
                    CASE
                        WHEN COUNT(*) = 0 THEN 0
                        ELSE ROUND(
                            COUNT(*) FILTER (
                                WHERE status = 'COLLECTED'
                            ) * 100.0 / COUNT(*),
                            2
                        )
                    END
                FROM collection_records
            ) AS collection_rate,


            -- COMPLAINTS
            (
                SELECT COUNT(*)
                FROM complaints
                WHERE status NOT IN ('RESOLVED', 'CLOSED')
            ) AS open_complaints,

            (
                SELECT COUNT(*)
                FROM complaints
                WHERE priority IN ('HIGH', 'URGENT')
                  AND status NOT IN ('RESOLVED', 'CLOSED')
            ) AS high_priority_complaints,


            -- INCIDENTS
            (
                SELECT COUNT(*)
                FROM incidents
                WHERE status NOT IN ('RESOLVED', 'CLOSED')
            ) AS active_incidents;
    """)

    result = db.execute(query)
    row = result.mappings().one()

    return {
        "total_households": row["total_households"],
        "active_households": row["active_households"],

        "total_billed": float(row["total_billed"]),
        "total_paid": float(row["total_paid"]),
        "total_outstanding": float(row["total_outstanding"]),

        "total_collections": row["total_collections"],
        "collected_collections": row["collected_collections"],
        "missed_collections": row["missed_collections"],
        "collection_rate": float(row["collection_rate"]),

        "open_complaints": row["open_complaints"],
        "high_priority_complaints": row["high_priority_complaints"],

        "active_incidents": row["active_incidents"],
    }

@router.get(
    "/routes",
    response_model=list[RoutePerformanceResponse]
)
def get_route_performance(
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT
            r.route_id,
            r.route_name,

            COUNT(DISTINCT h.household_id)
                AS total_households,

            COUNT(cr.collection_record_id)
                AS total_collections,

            COUNT(cr.collection_record_id)
                FILTER (WHERE cr.status = 'COLLECTED')
                AS collected_collections,

            COUNT(cr.collection_record_id)
                FILTER (WHERE cr.status = 'MISSED')
                AS missed_collections,

            CASE
                WHEN COUNT(cr.collection_record_id) = 0
                    THEN 0
                ELSE ROUND(
                    COUNT(cr.collection_record_id)
                    FILTER (
                        WHERE cr.status = 'COLLECTED'
                    ) * 100.0
                    / COUNT(cr.collection_record_id),
                    2
                )
            END AS collection_rate

        FROM routes r

        LEFT JOIN households h
            ON h.route_id = r.route_id

        LEFT JOIN collection_schedules cs
            ON cs.route_id = r.route_id

        LEFT JOIN collection_records cr
            ON cr.schedule_id = cs.schedule_id
            AND cr.household_id = h.household_id

        GROUP BY
            r.route_id,
            r.route_name

        ORDER BY
            collection_rate ASC,
            r.route_id;
    """)

    result = db.execute(query)

    return result.mappings().all()
@router.get(
    "/workers",
    response_model=list[WorkerPerformanceResponse]
)
def get_worker_performance(
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT
            w.worker_id,
            w.full_name AS worker_name,

            COUNT(cr.collection_record_id)
                AS total_collections,

            COUNT(cr.collection_record_id)
                FILTER (WHERE cr.status = 'COLLECTED')
                AS collected_collections,

            COUNT(cr.collection_record_id)
                FILTER (WHERE cr.status = 'MISSED')
                AS missed_collections,

            CASE
                WHEN COUNT(cr.collection_record_id) = 0
                    THEN 0
                ELSE ROUND(
                    COUNT(cr.collection_record_id)
                    FILTER (
                        WHERE cr.status = 'COLLECTED'
                    ) * 100.0
                    / COUNT(cr.collection_record_id),
                    2
                )
            END AS collection_rate

        FROM workers w

        JOIN collection_assignments ca
            ON ca.worker_id = w.worker_id

        JOIN collection_schedules cs
            ON cs.assignment_id = ca.assignment_id

        LEFT JOIN collection_records cr
            ON cr.schedule_id = cs.schedule_id

        WHERE w.role = 'COLLECTOR'

        GROUP BY
            w.worker_id,
            w.full_name

        ORDER BY
            collection_rate ASC,
            w.worker_id;
    """)

    result = db.execute(query)

    return result.mappings().all()