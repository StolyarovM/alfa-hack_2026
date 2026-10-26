from pydantic import BaseModel, Field, field_validator
class ApplicationCreate(BaseModel):
    business_name: str = Field(min_length=2, max_length=200)
    inn: str
    industry: str = Field(min_length=2, max_length=120)
    age_ip: int = Field(ge=18, le=100)
    monthly_revenue: int = Field(gt=0)
    monthly_credit_payments: int = Field(ge=0)
    has_overdue: bool
    has_collateral: bool
    product_type: str
    requested_amount: int = Field(gt=0)
    @field_validator("inn")
    @classmethod
    def validate_inn(cls, value: str):
        value = value.strip()
        if not (len(value) in (10, 12) and value.isdigit()):
            raise ValueError("ИНН должен содержать 10 или 12 цифр")
        return value
