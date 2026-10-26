
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Text
from app.db.base import Base
class Survey(Base):
    __tablename__ = "surveys"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    goal: Mapped[str] = mapped_column(String(80))
    answers_json: Mapped[str] = mapped_column(Text)
