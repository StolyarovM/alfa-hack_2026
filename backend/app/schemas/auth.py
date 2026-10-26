from pydantic import BaseModel, EmailStr, Field, field_validator

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=3, max_length=200)
    email: EmailStr
    phone: str = Field(min_length=5, max_length=32)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def clean_name(cls, value: str):
        value = " ".join(value.split())
        if len(value.split()) < 2:
            raise ValueError("Укажите имя и фамилию")
        return value

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
