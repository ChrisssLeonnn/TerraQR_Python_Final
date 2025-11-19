from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import schemas, models
from app.db.database import get_db
from app.services import personas_service, qr_generator_service, pdf_generator_service, email_service, eventos_service

router = APIRouter()

@router.post("/send-pass", status_code=status.HTTP_200_OK)
async def send_qr_pass_by_email(
    request: schemas.QREmailRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generates a QR pass PDF for a person and sends it to their email.
    This endpoint is intended to be called by external services like ManyChat.
    """
    persona = await personas_service.get_persona_by_email(db, request.email)
    if not persona:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona no encontrada con ese correo electrónico.")

    qr_url = personas_service.generate_qr_url(persona.QRToken)
    qr_image_data = qr_generator_service.generate_qr_image(qr_url)

    # Get event name for the PDF context
    evento = await eventos_service.get_evento_by_key(db, request.evento_key)
    event_name = evento.NombreEvento if evento else "Evento Desconocido"

    pdf_data = pdf_generator_service.generate_pass_pdf(persona, qr_image_data, event_name)

    persona_full_name = f"{persona.Nombre} {persona.ApellidoPaterno} {persona.ApellidoMaterno}"
    email_sent = await email_service.send_pdf_email(
        to_email=persona.Correo,
        persona_name=persona_full_name,
        pdf_data=pdf_data,
        event_name=event_name
    )

    if not email_sent:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al enviar el correo electrónico con el pase QR.")

    return {"status": "success", "message": f"Pase QR enviado a {persona.Correo}."}
