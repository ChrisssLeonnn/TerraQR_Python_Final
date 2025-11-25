from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from pydantic import ValidationError

from app.db import schemas, models
from app.db.database import get_db
from app.services import personas_service, pdf_service
from app.core.security import get_current_operador
from app.core.config import settings

router = APIRouter()

@router.post("/", response_model=schemas.PersonaWithPDF, status_code=status.HTTP_201_CREATED)
async def register_new_persona(
    persona_in: schemas.PersonaCreate,
    db: AsyncSession = Depends(get_db),
    current_operador: models.Operador = Depends(get_current_operador)
):
    """
    Registers a new person and returns data including a durable URL
    to generate the QR code PDF.
    Requires operator authentication.
    """
    try:
        new_persona = await personas_service.create_persona(db, persona_in)
        
        # Construct the durable URL to our new dynamic PDF endpoint
        pdf_url = f"{settings.TERRAQR_BASE_URL}/api/personas/qr/{new_persona.PersonaId}"

        # Convert the SQLAlchemy model to a Pydantic Persona model
        persona_data = schemas.Persona.from_orm(new_persona)

        # Create the final response object that matches the response_model
        response_object = schemas.PersonaWithPDF(
            **persona_data.dict(),
            pdf_url=pdf_url
        )
        
        return response_object

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
        # Log the exception for debugging
        print(f"Unexpected error in register_new_persona: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Unexpected error", "message": str(e)}
        )

@router.get("/qr/{persona_id}")
async def generate_persona_qr_pdf(
    persona_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Generates and returns a PDF with the QR code for a given person ID.
    This endpoint is designed to be used as a durable link.
    """
    persona = await personas_service.get_persona_by_id(db, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada.")

    # The URL to be encoded in the QR code itself
    qr_encode_url = personas_service.generate_qr_url(persona.QRToken)
    
    # Generate PDF in memory
    pdf_bytes = pdf_service.generate_qr_pdf(persona, qr_encode_url)
    
    # Return the PDF as a response
    return Response(
        content=pdf_bytes, 
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=\"{persona.PersonaId}.pdf\""}
    )
