from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from pwdlib import PasswordHash

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 20

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
password_hash = PasswordHash.recommended()
# Temporary in-memory database.
users = [
    {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin",
        "hashed_password": password_hash.hash("1234")
    },
    {
            "id": 2,
            "username": "anant",
            "email": "anant@example.com",
            "first_name": "Anant",
            "last_name": "shah",
            "role": "user",
            "hashed_password": password_hash.hash("123")
    }
]


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


def authenticate_user(username: str, password: str):
    user = next((item for item in users if item["username"] == username), None)
    if user and password_hash.verify(password, user["hashed_password"]):
        return user
    return None


def create_access_token(user: dict):
    payload = {
        "sub": user["username"],
        "id": user["id"],
        "role": user["role"],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate user.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = next((item for item in users if item["username"] == username), None)
        if user is None:
            raise credentials_error
        return user
    except JWTError as exc:
        raise credentials_error from exc


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(request: CreateUserRequest):
    if any(item["username"] == request.username for item in users):
        raise HTTPException(status_code=400, detail="Username already exists.")
    users.append({
        "id": len(users) + 1,
        "username": request.username,
        "email": request.email,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "role": request.role,
        "hashed_password": password_hash.hash(request.password),
    })
    return {"message": "User created successfully."}


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(user), "token_type": "bearer"}


@router.get("/me")
async def read_current_user(current_user: Annotated[dict, Depends(get_current_user)]):
    return {key: value for key, value in current_user.items() if key != "hashed_password"}