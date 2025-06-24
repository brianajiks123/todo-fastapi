import os, secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from crud import get_user_by_username
from dotenv import load_dotenv

load_dotenv()

# Ensure SECRET_KEY is always a string
SECRET_KEY: str = os.getenv("SECRET_KEY") or secrets.token_hex(32)

# Save SECRET_KEY to .env only if it was newly generated
if os.getenv("SECRET_KEY") is None:
    try:
        # Read existing .env content
        env_content = {}

        if os.path.exists(".env"):
            with open(".env", "r") as env_file:
                for line in env_file:
                    if line.strip() and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        env_content[key] = value

        # Only append SECRET_KEY if it doesn't exist
        if "SECRET_KEY" not in env_content:
            with open(".env", "a") as env_file:
                env_file.write(f"\nSECRET_KEY={SECRET_KEY}")

            print("Generated and saved new SECRET_KEY to .env")
    except Exception as e:
        print(f"Warning: Could not save SECRET_KEY to .env: {e}")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)

    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        username = payload.get("sub")

        if not isinstance(username, str):
            raise credentials_exception

        token_data = TokenData(username = username)
    except JWTError:
        raise credentials_exception

    if token_data.username is None:
        raise credentials_exception

    user = get_user_by_username(db, username = token_data.username)

    if user is None:
        raise credentials_exception

    return user
