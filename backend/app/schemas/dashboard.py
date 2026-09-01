from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    total_households: int
    active_households: int

    total_billed: float
    total_paid: float
    total_outstanding: float

    total_collections: int
    collected_collections: int
    missed_collections: int
    collection_rate: float

    open_complaints: int
    high_priority_complaints: int

    active_incidents: int


class RoutePerformanceResponse(BaseModel):
    route_id: int
    route_name: str
    total_households: int
    total_collections: int
    collected_collections: int
    missed_collections: int
    collection_rate: float


class WorkerPerformanceResponse(BaseModel):
    worker_id: int
    worker_name: str
    total_collections: int
    collected_collections: int
    missed_collections: int
    collection_rate: float