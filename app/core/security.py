import hashlib
from datetime import datetime, timedelta
from typing import Optional, Union, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db import models, schemas
from app.db.database import get_db
from app.services import operadores_service

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    """Verifies a plain password against a hashed one."""
    return get_password_hash(plain_password) == hashed_password

def get_password_hash(password: str) -> bytes:
    """Hashes a password using SHA256, returns the binary hash."""
    return hashlib.sha256(password.encode('utf-8')).digest()

def hash_curp(curp: str) -> bytes:
    """Hashes a CURP using SHA256 after converting to uppercase."""
    return hashlib.sha256(curp.upper().encode('utf-8')).digest()

# JWT Token Creation
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Dependency to get current user
async def get_current_operador(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> models.Operador:
    """
    Decodes JWT token to get the current operator.
    Raises HTTPException if the token is invalid or the operator doesn't exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        operador_id: str = payload.get("sub")
        if operador_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(sub=operador_id)
    except JWTError:
        raise credentials_exception
    
    operador = await operadores_service.get_operador_by_id(db, operador_id=token_data.sub)
    if operador is None:
        raise credentials_exception
    if not operador.Activo:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return operador
