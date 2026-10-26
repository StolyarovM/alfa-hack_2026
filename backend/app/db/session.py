
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base import Base
from app.models import user, company, application, survey, verification, scoring_result, audit_event  # noqa: F401

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    # Небольшая совместимая миграция для локального MVP, если volume уже был создан старой версией.
    inspector = inspect(engine)
    with engine.begin() as conn:
        user_columns = {c["name"] for c in inspector.get_columns("users")}
        company_columns = {c["name"] for c in inspector.get_columns("companies")}
        dialect = engine.dialect.name
        if "full_name" not in user_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR(200) NOT NULL DEFAULT 'Пользователь'"))
        if "email" not in user_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(255) NOT NULL DEFAULT ''"))
        if "phone" not in user_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(32) NOT NULL DEFAULT ''"))
        if "business_name" not in company_columns:
            conn.execute(text("ALTER TABLE companies ADD COLUMN business_name VARCHAR(200) NOT NULL DEFAULT 'Мой бизнес'"))
    from app.models.user import User
    from app.core.security import hash_password
    with SessionLocal() as db:
        # Сохраняем совместимость со старой локальной учётной записью.
        primary = db.query(User).filter_by(username="demo").first()
        if not primary:
            primary = User(
                username="demo",
                email="demo@example.local",
                full_name="Иван Иванов",
                phone="+7 900 000-00-00",
                password_hash=hash_password("demo12345"),
                inn="",
                business_name="",
            )
            db.add(primary)
        elif primary.full_name in (None, "", "Пользователь", "Демо Пользователь"):
            primary.full_name = "Иван Иванов"
            primary.email = primary.email or "demo@example.local"
            primary.phone = primary.phone or "+7 900 000-00-00"

        # Дополнительная учётная запись для проверки независимой истории заявок.
        secondary_email = "maria.smirnova@example.local"
        secondary = db.query(User).filter_by(username=secondary_email).first()
        if not secondary:
            db.add(User(
                username=secondary_email,
                email=secondary_email,
                full_name="Мария Смирнова",
                phone="+7 901 000-00-00",
                password_hash=hash_password("Business2026!"),
                inn="",
                business_name="",
            ))
        db.commit()
