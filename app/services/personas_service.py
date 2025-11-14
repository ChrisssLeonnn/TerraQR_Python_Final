from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID, uuid4
from typing import Optional

from app.db import models, schemas
from app.core.security import hash_curp
from app.core.config import settings

async def get_persona_by_qr_token(db: AsyncSession, qr_token: UUID) -> Optional[models.Persona]:
    """Fetches a person by their QRToken."""
    result = await db.execute(select(models.Persona).filter(models.Persona.QRToken == qr_token))
    return result.scalars().first()

async def get_persona_by_curp_hash(db: AsyncSession, curp_hash: bytes) -> Optional[models.Persona]:
    """Checks if a person exists with the given CURP hash."""
    result = await db.execute(select(models.Persona).filter(models.Persona.CURPHash == curp_hash))
    return result.scalars().first()

async def create_persona(db: AsyncSession, persona_in: schemas.PersonaCreate) -> models.Persona:
    """
    Creates a new person in the database.
    - Hashes the CURP.
    - Generates PersonaId and QRToken.
    - Saves the new person record.
    """
    curp_hash_bytes = hash_curp(persona_in.CURP)
    
    # Check if CURP already exists
    existing_persona = await get_persona_by_curp_hash(db, curp_hash_bytes)
    if existing_persona:
        raise ValueError("A person with this CURP already exists.")

    db_persona = models.Persona(
        PersonaId=uuid4(),
        QRToken=uuid4(),
        CURPHash=curp_hash_bytes,
        Nombre=persona_in.Nombre,
        ApellidoPaterno=persona_in.ApellidoPaterno,
        ApellidoMaterno=persona_in.ApellidoMaterno,
        FechaNacimiento=persona_in.FechaNacimiento,
        Genero=persona_in.Genero,
        Colonia=persona_in.Colonia,
        Correo=persona_in.Correo,
        Telefono=persona_in.Telefono,
    )
    
    db.add(db_persona)
    await db.commit()
    await db.refresh(db_persona)
    
    return db_persona

def generate_qr_url(qr_token: UUID) -> str:
    """Generates the official TerraQR validation URL."""
    return f"{settings.TERRAQR_BASE_URL}/scan/{str(qr_token)}" # Changed /qr/validate to /scan
