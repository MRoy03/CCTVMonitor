import uuid

from pydantic import BaseModel, field_validator

from cip.services.rule_engine.schema import validate_actions, validate_condition


class RuleCreate(BaseModel):
    camera_id: str
    name: str
    conditions: dict
    actions: list[dict]
    enabled: bool = True
    cooldown_seconds: int = 300

    @field_validator("conditions")
    @classmethod
    def _validate_conditions(cls, value: dict) -> dict:
        validate_condition(value)
        return value

    @field_validator("actions")
    @classmethod
    def _validate_actions(cls, value: list[dict]) -> list[dict]:
        validate_actions(value)
        return value


class RuleUpdate(BaseModel):
    name: str | None = None
    conditions: dict | None = None
    actions: list[dict] | None = None
    enabled: bool | None = None
    cooldown_seconds: int | None = None

    @field_validator("conditions")
    @classmethod
    def _validate_conditions(cls, value: dict | None) -> dict | None:
        if value is not None:
            validate_condition(value)
        return value

    @field_validator("actions")
    @classmethod
    def _validate_actions(cls, value: list[dict] | None) -> list[dict] | None:
        if value is not None:
            validate_actions(value)
        return value


class RuleResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    camera_id: uuid.UUID | None
    name: str
    conditions: dict
    actions: list
    enabled: bool
    cooldown_seconds: int

    model_config = {"from_attributes": True}
