from pydantic import BaseModel, ConfigDict
from typing import Optional


class RouteResponse(BaseModel):
    route_id: int
    neighborhood_id: int
    route_name: str
    description: Optional[str] = None
    status: str

    model_config = ConfigDict(from_attributes=True)