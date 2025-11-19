from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID, uuid4
from typing import Optional

from app.db import models, schemas
from app.services import personas_service, eventos_service

async def get_existing_asistencia(db: AsyncSession, persona_id: UUID, evento_id: UUID) -> Optional[models.Asistencia]:
    """Checks if a person has already checked into a specific event."""
    result = await db.execute(
        select(models.Asistencia).filter_by(PersonaId=persona_id, EventoId=evento_id)
    )
    return result.scalars().first()

async def register_asistencia(db: AsyncSession, qr_token: UUID, evento_key: str, cantidad_acompanantes: Optional[int] = None) -> models.Asistencia:
    """
    Registers a person's attendance at an event.
    1. Finds person by QR token.
    2. Finds event by EventoKey.
    3. Checks for existing check-in.
    4. Creates Asistencia record.
    """
    persona = await personas_service.get_persona_by_qr_token(db, qr_token)
    if not persona:
        raise ValueError("Persona no encontrada con el QR token proporcionado.")

    evento = await eventos_service.get_evento_by_key(db, evento_key)
    if not evento:
        raise ValueError(f"Evento '{evento_key}' no encontrado.")

    existing_asistencia = await get_existing_asistencia(db, persona.PersonaId, evento.EventoId)
    if existing_asistencia:
        raise ValueError("Esta persona ya tiene registrada su asistencia a este evento.")

    # Create Asistencia
    db_asistencia = models.Asistencia(
        AsistenciaId=uuid4(),
        PersonaId=persona.PersonaId,
        EventoId=evento.EventoId,
        CantidadAcompanantes=cantidad_acompanantes # New field
    )
    db.add(db_asistencia)

    await db.commit()
    await db.refresh(db_asistencia)
    
    return db_asistencia