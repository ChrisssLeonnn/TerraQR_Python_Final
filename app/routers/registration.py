from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import schemas, models
from app.db.database import get_db
from app.services import personas_service, eventos_service # Removed qr_generator_service, pdf_generator_service, email_service

router = APIRouter()

@router.post("/register-group", status_code=status.HTTP_201_CREATED, response_model=schemas.WhatsAppQRResponse) # Changed response model
async def register_group(
    group_request: schemas.GroupRegistrationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Registers an adult and their accompanying children/seniors.
    Returns the QR URL and phone number for WhatsApp delivery.
    Intended to be called by external services like ManyChat.
    """
    try:
        # 1. Create the adult and companions in the database
        adulto_persona = await personas_service.create_group_registration(db, group_request)

        # 2. Generate QR URL for the adult
        qr_url = personas_service.generate_qr_url(adulto_persona.QRToken)

        # 3. Return data for ManyChat to send via WhatsApp
        return {
            "status": "success",
            "message": f"Grupo registrado. QR URL generado para {adulto_persona.Nombre}.",
            "qr_url": qr_url,
            "phone_number": adulto_persona.Telefono, # Assuming this is the WhatsApp number
            "persona_id": adulto_persona.PersonaId,
            "qr_token": adulto_persona.QRToken
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Error during group registration: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ocurrió un error inesperado durante el registro del grupo.")