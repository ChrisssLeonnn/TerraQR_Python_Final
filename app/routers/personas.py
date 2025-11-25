from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db import schemas, models
from app.db.database import get_db
from app.services import personas_service
from app.core.security import get_current_operador
from app.core.config import settings

router = APIRouter()

from fastapi.responses import Response
from app.services import pdf_service

from fastapi.responses import JSONResponse
from pydantic import ValidationError

# ... (the rest of the imports)

@router.post("/", response_model=schemas.PersonaWithPDF, status_code=status.HTTP_201_CREATED)
async def register_new_persona(
    persona_in: schemas.PersonaCreate,
    db: AsyncSession = Depends(get_db),
    current_operador: models.Operador = Depends(get_current_operador)
):
    """
    Registers a new person, creates a PDF with a QR code, 
    and returns the person's data along with the URL to the PDF.
    Requires operator authentication.
    """
    try:
        new_persona = await personas_service.create_persona(db, persona_in)
        qr_url = personas_service.generate_qr_url(new_persona.QRToken)
        
        pdf_path = pdf_service.generate_qr_pdf(new_persona, qr_url)
        
        # Create the full URL for the PDF
        pdf_url = f"{settings.TERRAQR_BASE_URL}/{pdf_path.replace('app/', '')}"

        # Convert the SQLAlchemy model to a Pydantic Persona model
        persona_data = schemas.Persona.from_orm(new_persona)

        # Create the final response object that matches the response_model
        response_object = schemas.PersonaWithPDF(
            **persona_data.dict(),
            pdf_url=pdf_url
        )
        
        # By returning the Pydantic model, we let FastAPI handle the JSON serialization
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
        return JSONResponse(
            status_code=500,
            content={"error": "Unexpected error", "message": str(e)}
        )


from typing import List

# ... (the rest of the imports)
