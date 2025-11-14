from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db import schemas, models
from app.db.database import get_db
from app.services import eventos_service
from app.core.security import get_current_operador

router = APIRouter()

@router.post("/", response_model=schemas.Evento, status_code=status.HTTP_201_CREATED)
async def create_new_evento(
    evento_in: schemas.EventoCreate,
    db: AsyncSession = Depends(get_db),
    current_operador: models.Operador = Depends(get_current_operador)
):
    """
    Creates a new event. Requires operator authentication.
    """
    try:
        new_evento = await eventos_service.create_evento(db, evento_in)
        return new_evento
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create event.")

@router.get("/", response_model=List[schemas.Evento])
async def get_all_eventos_list(
    db: AsyncSession = Depends(get_db),
    current_operador: models.Operador = Depends(get_current_operador)
):
    """
    Retrieves a list of all events. Requires operator authentication.
    """
    eventos = await eventos_service.get_all_eventos(db)
    return eventos
