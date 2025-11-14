from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional # Added Optional
from uuid import uuid4

from app.db import models, schemas

async def get_all_eventos(db: AsyncSession) -> List[models.Evento]:
    """Fetches all events."""
    result = await db.execute(
        select(models.Evento)
        .order_by(models.Evento.Fecha.desc())
    )
    return result.scalars().all()

async def get_evento_by_key(db: AsyncSession, evento_key: str) -> Optional[models.Evento]:
    """Fetches an event by its EventoKey."""
    result = await db.execute(
        select(models.Evento)
        .filter(models.Evento.EventoKey == evento_key)
    )
    return result.scalars().first()

async def create_evento(db: AsyncSession, evento_in: schemas.EventoCreate) -> models.Evento:
    """
    Creates a new event.
    """
    db_evento = models.Evento(
        EventoId=uuid4(),
        EventoKey=evento_in.EventoKey,
        NombreEvento=evento_in.NombreEvento,
        Fecha=evento_in.Fecha,
    )
    
    db.add(db_evento)
    await db.commit()
    await db.refresh(db_evento)
    
    return db_evento