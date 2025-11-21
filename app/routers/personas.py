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

from fastapi.responses import JSONResponse
from pydantic import ValidationError

# ... (the rest of the imports)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_new_persona(
    persona_in: schemas.PersonaCreate,
    db: AsyncSession = Depends(get_db),
    current_operador: models.Operador = Depends(get_current_operador)
):
    """
    Registers a new person, creates a PDF with a QR code, 
    and returns a JSON response with the person's data and the URL to the PDF.
    Requires operator authentication.
    """
    try:
        new_persona = await personas_service.create_persona(db, persona_in)
        qr_url = personas_service.generate_qr_url(new_persona.QRToken)
        
        pdf_path = pdf_service.generate_qr_pdf(new_persona, qr_url)
        
        # Create the full URL for the PDF
        pdf_url = f"{settings.TERRAQR_BASE_URL}/{pdf_path.replace('app/', '')}"

        response_data = schemas.Persona.from_orm(new_persona).dict()
        response_data['pdf_url'] = pdf_url
        
        return JSONResponse(content=response_data, status_code=201)

    except ValidationError as e:
        return JSONResponse(
            status_code=422,
            content={"error": "Validation error", "details": e.errors()}
        )
    except ValueError as e:
        return JSONResponse(
            status_code=409,
            content={"error": "Conflict", "message": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Unexpected error", "message": str(e)}
        )


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
    current_operador: models.Operador = Depends(get_current_operador)
):
    """
    Deletes all persons registered with a given phone number. Requires operator authentication.
    """
    deleted_count = await personas_service.delete_personas_by_telefono(db, telefono)
    if deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron personas con ese número de teléfono.")
    
    return {"message": f"Se eliminaron {deleted_count} personas."}
