from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services import personas_service
from fastapi import Depends

router = APIRouter()

@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook to receive messages from WhatsApp Cloud API (via ManyChat).
    It extracts the user's phone number and ManyChat contact ID and
    updates the corresponding Persona record in the database.
    """
    body = await request.json()
    
    # The structure of the webhook payload can vary.
    # This is an example based on a common structure.
    # You will need to inspect the actual payload from ManyChat to get the correct paths.
    try:
        contact_id = body['contact']['id']
        phone_number = body['contact']['phone'] # Assuming ManyChat provides the phone number here
        
        # Find the persona by contact ID
        persona = await personas_service.get_persona_by_contact_id(db, contact_id)
        
        if persona and not persona.Telefono:
            # Update the persona with the phone number
            persona.Telefono = phone_number
            await db.commit()
            
    except KeyError:
        # Handle cases where the payload structure is different
        pass
        
    return {"status": "ok"}

@router.get("/whatsapp")
async def verify_webhook(request: Request):
    """
    Webhook verification for WhatsApp Cloud API.
    """
    # This is for the initial verification of the webhook URL.
    # You need to get the VERIFY_TOKEN from your Meta for Developers app configuration.
    VERIFY_TOKEN = "your_verify_token" # Replace with your verify token

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return int(challenge)
        else:
            raise HTTPException(status_code=403, detail="Verification token mismatch")
    
    raise HTTPException(status_code=400, detail="Missing parameters")
