from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey
from app.db.base import Base

class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    inn: Mapped[str] = mapped_column(String(12), index=True)
    business_name: Mapped[str] = mapped_column(String(200), default="Мой бизнес")
    business_age_months: Mapped[int] = mapped_column(Integer, default=24)
    industry: Mapped[str] = mapped_column(String(120), default="Другая отрасль")
    monthly_turnover: Mapped[int] = mapped_column(Integer, default=400000)
    employees: Mapped[int] = mapped_column(Integer, default=3)
    active_credits: Mapped[int] = mapped_column(Integer, default=0)
    bank_account_months: Mapped[int] = mapped_column(Integer, default=12)
