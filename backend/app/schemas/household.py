from pydantic import BaseModel, ConfigDict


class HouseholdResponse(BaseModel):
    household_id: int
    neighborhood_id: int
    route_id: int | None
    house_number: str
    street: str
    monthly_fee: float
    collection_preference: str
    service_status: str

    model_config = ConfigDict(from_attributes=True)