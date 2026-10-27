import uuid

from pydantic import BaseModel, field_validator


class ZoneCreate(BaseModel):
    name: str
    polygon_coordinates: list[list[float]]  # [[x, y], ...] normalized 0-1

    @field_validator("polygon_coordinates")
    @classmethod
    def at_least_a_triangle(cls, value: list[list[float]]) -> list[list[float]]:
        if len(value) < 3:
            raise ValueError("A zone polygon needs at least 3 points")
        return value


class ZoneResponse(BaseModel):
    id: uuid.UUID
    camera_id: uuid.UUID
    name: str
    polygon_coordinates: list[list[float]]

    model_config = {"from_attributes": True}
