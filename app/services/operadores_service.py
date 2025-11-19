from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import Optional

from app.db import models
from app.core.hashing import verify_password

async def get_operador_by_id(db: AsyncSession, operador_id: str) -> Optional[models.Operador]:
    """Fetches an operator by their UUID."""
    result = await db.execute(select(models.Operador).filter(models.Operador.OperadorId == UUID(operador_id)))
    return result.scalars().first()

async def get_operador_by_usuario(db: AsyncSession, usuario: str) -> Optional[models.Operador]:
    """Fetches an operator by their username."""
    result = await db.execute(select(models.Operador).filter(models.Operador.Usuario == usuario))
    return result.scalars().first()

async def authenticate_operador(db: AsyncSession, usuario: str, contrasena: str) -> Optional[models.Operador]:
    """
    Authenticates an operator.
    
    1. Fetches the operator by username.
    2. Verifies the password hash.
    3. Checks if the operator is active.
    
    Returns the operator model if successful, otherwise None.
    """
    operador = await get_operador_by_usuario(db, usuario=usuario)
    if not operador:
        return None
    
    if not verify_password(contrasena, operador.ContrasenaHash):
        return None
        
    if not operador.Activo:
        return None
        
    return operador
