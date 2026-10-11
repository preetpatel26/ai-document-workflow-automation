from datetime import date, datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field, field_validator

class ShipmentRecord(BaseModel):
    shipment_reference: str = Field(min_length=2, max_length=100)
    shipper_name: str = Field(min_length=2, max_length=200)
    pickup_location: str = Field(min_length=2, max_length=300)
    delivery_location: str = Field(min_length=2, max_length=300)
    pickup_date: date
    package_count: int = Field(gt=0, le=100000)
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("shipment_reference", "shipper_name", "pickup_location", "delivery_location")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

class ProcessRequest(BaseModel):
    document_text: str = Field(min_length=10, max_length=50000)
    send_to_downstream: bool = False

class ProcessResponse(BaseModel):
    status: Literal["processed", "review_required", "downstream_failed"]
    record: ShipmentRecord | None = None
    review_reasons: list[str] = Field(default_factory=list)
    downstream_status_code: int | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message: str
