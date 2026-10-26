
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text
from app.db.base import Base
class Application(Base):
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    inn: Mapped[str] = mapped_column(String(12))
    age_ip: Mapped[int] = mapped_column(Integer)
    monthly_revenue: Mapped[int] = mapped_column(Integer)
    monthly_credit_payments: Mapped[int] = mapped_column(Integer)
    has_overdue: Mapped[bool] = mapped_column(default=False)
    has_collateral: Mapped[bool] = mapped_column(default=False)
    product_type: Mapped[str] = mapped_column(String(80))
    requested_amount: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(40), default="SUBMITTED")
    outcome: Mapped[str | None] = mapped_column(String(200), nullable=True)
    risk: Mapped[float | None] = mapped_column(Float, nullable=True)
    scoring_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
