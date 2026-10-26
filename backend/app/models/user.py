from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # username оставлен для совместимости с уже созданной демо-базой.
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(200), default="Пользователь")
    email: Mapped[str] = mapped_column(String(255), default="", index=True)
    phone: Mapped[str] = mapped_column(String(32), default="")
    # Устаревшие поля нужны только для совместимости с существующей БД.
    # Больше не используются как данные профиля пользователя.
    inn: Mapped[str] = mapped_column(String(12), default="")
    business_name: Mapped[str] = mapped_column(String(200), default="")
