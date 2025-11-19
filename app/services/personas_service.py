from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID, uuid4
from typing import Optional, List

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

async def get_persona_by_email(db: AsyncSession, email: str) -> Optional[models.Persona]:
    """Fetches a person by their email address."""
    result = await db.execute(select(models.Persona).filter(models.Persona.Correo == email))
    return result.scalars().first()

async def create_persona(db: AsyncSession, persona_in: schemas.PersonaCreate, adulto_responsable_id: Optional[UUID] = None, inherit_contact_info: bool = False) -> models.Persona:
    """
    Creates a new person in the database.
    - Hashes the CURP if provided.
    - Generates PersonaId and QRToken.
    - Links to an adult responsible if provided.
    - Inherits contact info from adult if inherit_contact_info is True.
    """
    curp_hash_bytes = None
    if persona_in.CURP:
        curp_hash_bytes = hash_curp(persona_in.CURP)
        # Check if CURP already exists for adults
        if persona_in.TipoPersona == "Adulto":
            existing_persona = await get_persona_by_curp_hash(db, curp_hash_bytes)
            if existing_persona:
                raise ValueError("A person with this CURP already exists.")

    # Handle inherited contact info for companions
    colonia = persona_in.Colonia
    correo = persona_in.Correo
    telefono = persona_in.Telefono
    
    if inherit_contact_info and adulto_responsable_id:
        adulto = await db.get(models.Persona, adulto_responsable_id)
        if adulto:
            colonia = adulto.Colonia
            correo = adulto.Correo
            telefono = adulto.Telefono

    db_persona = models.Persona(
        PersonaId=uuid4(),
        QRToken=uuid4(),
        CURPHash=curp_hash_bytes,
        Nombre=persona_in.Nombre,
        ApellidoPaterno=persona_in.ApellidoPaterno,
        ApellidoMaterno=persona_in.ApellidoMaterno,
        FechaNacimiento=persona_in.FechaNacimiento,
        Genero=persona_in.Genero,
        Colonia=colonia, # Use inherited or provided
        Correo=correo,   # Use inherited or provided
        Telefono=telefono, # Use inherited or provided
        CodigoPostal=persona_in.CodigoPostal, # New field
        TipoPersona=persona_in.TipoPersona,
        AdultoResponsableId=adulto_responsable_id
    )
    
    db.add(db_persona)
    await db.commit()
    await db.refresh(db_persona)
    
    return db_persona

async def create_group_registration(db: AsyncSession, group_request: schemas.GroupRegistrationRequest) -> models.Persona:
    """
    Registers an adult and their accompanying children/seniors.
    Returns the registered adult Persona.
    """
    # 1. Create the adult persona
    adulto_persona = await create_persona(db, group_request.adulto)

    # 2. Create accompanying personas and link them to the adult
    if group_request.acompanantes:
        for acompanante_data in group_request.acompanantes:
            # Convert AcompananteCreate to PersonaCreate for reuse
            persona_create_data = schemas.PersonaCreate(
                Nombre=acompanante_data.Nombre,
                ApellidoPaterno=acompanante_data.ApellidoPaterno,
                ApellidoMaterno=acompanante_data.ApellidoMaterno,
                FechaNacimiento=acompanante_data.FechaNacimiento,
                Genero=acompanante_data.Genero,
                Colonia=group_request.adulto.Colonia, # Inherit from adult
                Correo=group_request.adulto.Correo,   # Inherit from adult
                Telefono=group_request.adulto.Telefono, # Inherit from adult
                CodigoPostal=acompanante_data.CodigoPostal,
                TipoPersona=acompanante_data.TipoPersona,
                CURP=None # Accompanantes don't have CURP
            )
            await create_persona(db, persona_create_data, adulto_responsable_id=adulto_persona.PersonaId, inherit_contact_info=True)
    
    return adulto_persona

def generate_qr_url(qr_token: UUID) -> str:
    """Generates the official TerraQR validation URL."""
    return f"{settings.TERRAQR_BASE_URL}/scan/{str(qr_token)}"