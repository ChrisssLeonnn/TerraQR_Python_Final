from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID, uuid4
from typing import Optional, List

from app.db import models, schemas
from app.core.config import settings

async def get_persona_by_qr_token(db: AsyncSession, qr_token: UUID) -> Optional[models.Persona]:
    """Fetches a person by their QRToken."""
    result = await db.execute(select(models.Persona).filter(models.Persona.QRToken == qr_token))
    return result.scalars().first()

async def get_persona_by_email(db: AsyncSession, email: str) -> Optional[models.Persona]:
    """Fetches a person by their email address."""
    result = await db.execute(select(models.Persona).filter(models.Persona.Correo == email))
    return result.scalars().first()

async def get_persona_by_telefono(db: AsyncSession, telefono: str) -> Optional[models.Persona]:
    """Fetches a person by their phone number."""
    result = await db.execute(select(models.Persona).filter(models.Persona.Telefono == telefono, models.Persona.TipoPersona == 'Adulto'))
    return result.scalars().first()

from datetime import date

async def create_persona(db: AsyncSession, persona_in: schemas.PersonaCreate) -> models.Persona:
    """
    Creates a new person in the database.
    - Calculates TipoPersona based on age.
    - Enforces that only one adult can be registered per phone number.
    - Generates PersonaId and QRToken.
    """
    # 1. Calculate age and TipoPersona
    today = date.today()
    age = today.year - persona_in.FechaNacimiento.year - ((today.month, today.day) < (persona_in.FechaNacimiento.month, persona_in.FechaNacimiento.day))
    
    if age < 18:
        tipo_persona = "Nino"
    elif 18 <= age < 60:
        tipo_persona = "Adulto"
    else:
        tipo_persona = "TerceraEdad"

    # 2. Enforce one adult per phone number
    if tipo_persona == 'Adulto':
        existing_persona = await get_persona_by_telefono(db, persona_in.Telefono)
        if existing_persona:
            raise ValueError("Ya existe un adulto registrado con este número de teléfono.")

    db_persona = models.Persona(
        PersonaId=uuid4(),
        QRToken=uuid4(),
        Nombre=persona_in.Nombre,
        ApellidoPaterno=persona_in.ApellidoPaterno,
        ApellidoMaterno=persona_in.ApellidoMaterno,
        FechaNacimiento=persona_in.FechaNacimiento,
        Genero=persona_in.Genero,
        Colonia=persona_in.Colonia,
        Correo=persona_in.Correo,
        Telefono=persona_in.Telefono,
        CodigoPostal=persona_in.CodigoPostal,
        TipoPersona=tipo_persona,
    )
    
    db.add(db_persona)
    await db.commit()
    await db.refresh(db_persona)
    
    return db_persona

def generate_qr_url(qr_token: UUID) -> str:
    """Generates the official TerraQR validation URL."""
    return f"{settings.TERRAQR_BASE_URL}/scan/{str(qr_token)}"