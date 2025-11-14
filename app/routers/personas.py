from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db import schemas, models
from app.db.database import get_db
from app.services import personas_service
from app.core.security import get_current_operador

router = APIRouter()

@router.post("/", response_model=schemas.PersonaWithQR, status_code=status.HTTP_201_CREATED)
async def register_new_persona(
    persona_in: schemas.PersonaCreate,
    db: AsyncSession = Depends(get_db),
    current_operador: models.Operador = Depends(get_current_operador)
):
    """
    Registers a new person. Requires operator authentication.
    """
    try:
        new_persona = await personas_service.create_persona(db, persona_in)
        qr_url = personas_service.generate_qr_url(new_persona.QRToken)
        
        # Manually construct the response model
        response_data = schemas.Persona.from_orm(new_persona).dict()
        response_data['qr_url'] = qr_url
        
        return schemas.PersonaWithQR(**response_data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")


@router.get("/{qr_token}", response_model=schemas.Persona)
async def get_persona_info(
    qr_token: UUID,
    db: AsyncSession = Depends(get_db),
    current_operador: models.Operador = Depends(get_current_operador)
):
    """
    Retrieves a person's data by their QR Token. Requires operator authentication.
    """
    persona = await personas_service.get_persona_by_qr_token(db, qr_token)
    if not persona:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona no encontrada.")
    
    return persona
