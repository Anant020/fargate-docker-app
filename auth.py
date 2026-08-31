from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Users


router = APIRouter(prefix="/auth", tags=["auth"])


SECRET_KEY = "197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 20


oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
password_hash = PasswordHash.recommended()


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db: Session):
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        return None

    if not password_hash.verify(password, user.hashed_password):
        return None

    return user


def create_access_token(user: Users):
    payload = {
        "sub": user.username,
        "id": user.id,
        "role": user.role,
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)]
):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate user.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")
        user_id = payload.get("id")

        if username is None or user_id is None:
            raise credentials_error

        return {
            "username": username,
            "id": user_id,
            "role": payload.get("role"),
        }

    except JWTError:
        raise credentials_error


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    db: db_dependency
):
    existing_user = (
        db.query(Users)
        .filter(Users.username == request.username)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists."
        )

    new_user = Users(
        username=request.username,
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        role=request.role,
        hashed_password=password_hash.hash(request.password),
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully."
    }


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency,
):
    user = authenticate_user(
        form_data.username,
        form_data.password,
        db
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user)

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.get("/me")
async def read_current_user(
    current_user: Annotated[dict, Depends(get_current_user)]
):
    return current_user