from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    organization_name: str
    email: EmailStr
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    organization_id: str
    email: str
    full_name: str | None
    role: str

    model_config = {"from_attributes": True}
