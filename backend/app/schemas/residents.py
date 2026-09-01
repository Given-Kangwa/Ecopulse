from pydantic import BaseModel, ConfigDict


class ResidentResponse(BaseModel):
    resident_id: int
    household_id: int
    full_name: str
    phone_number: str
    is_primary_contact: bool

    model_config = ConfigDict(from_attributes=True)