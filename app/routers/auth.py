from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.db import schemas
from app.db.database import get_db
from app.services import operadores_service
from app.core.security import create_access_token
from app.core.config import settings

router = APIRouter()

@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    db: AsyncSession = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Provides a JWT token for valid operator credentials.
    """
    operador = await operadores_service.authenticate_operador(
        db, usuario=form_data.username, contrasena=form_data.password
    )
    if not operador:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(operador.OperadorId)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
