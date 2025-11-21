from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db import schemas, models
from app.db.database import get_db
from app.services import personas_service
from app.core.security import get_current_operador

router = APIRouter()

from fastapi.responses import Response
from app.services import pdf_service

@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_new_persona(
    persona_in: schemas.PersonaCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Registers a new person and returns a PDF with the QR code.
    """
    try:
        new_persona = await personas_service.create_persona(db, persona_in)
        qr_url = personas_service.generate_qr_url(new_persona.QRToken)
        
        pdf_bytes = pdf_service.generate_qr_pdf(new_persona, qr_url)
        
        return Response(content=pdf_bytes, media_type="application/pdf")

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")


from typing import List

# ... (the rest of the imports)

@router.get("/telefono/{telefono}", response_model=List[schemas.Persona])
async def get_personas_by_telefono_api(
    telefono: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves a list of all persons registered with a given phone number.
    """
    personas = await personas_service.get_personas_by_telefono(db, telefono)
    return personas

@router.delete("/telefono/{telefono}", status_code=status.HTTP_200_OK)
async def delete_personas_by_telefono_api(
    telefono: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Deletes all persons registered with a given phone number.
    """
    deleted_count = await personas_service.delete_personas_by_telefono(db, telefono)
    if deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron personas con ese número de teléfono.")
    
    return {"message": f"Se eliminaron {deleted_count} personas."}
