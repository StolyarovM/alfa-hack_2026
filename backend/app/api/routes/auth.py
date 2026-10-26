from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.core.security import verify_password, hash_password, create_access_token, decode_access_token

router = APIRouter()
bearer = HTTPBearer(auto_error=False)

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not credentials:
        raise HTTPException(401, "Требуется авторизация")
    subject = decode_access_token(credentials.credentials)
    if not subject:
        raise HTTPException(401, "Токен недействителен или истёк")
    try:
        user_id = int(subject)
    except ValueError:
        raise HTTPException(401, "Токен недействителен")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(401, "Пользователь не найден")
    return user

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = str(payload.email).lower().strip()
    if db.query(User).filter((User.email == email) | (User.username == email)).first():
        raise HTTPException(409, "Пользователь с таким email уже зарегистрирован")
    user = User(
        username=email,
        email=email,
        full_name=payload.full_name.strip(),
        phone=payload.phone.strip(),
        password_hash=hash_password(payload.password),
        inn="",
        business_name="",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(str(user.id)))

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    login_value = payload.username.strip().lower()
    user = db.query(User).filter((User.email == login_value) | (User.username == login_value)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Неверный email/логин или пароль")
    return TokenResponse(access_token=create_access_token(str(user.id)))

@router.post("/logout")
def logout():
    return {"ok": True}

@router.get("/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "full_name": user.full_name, "email": user.email, "phone": user.phone, "username": user.username}
