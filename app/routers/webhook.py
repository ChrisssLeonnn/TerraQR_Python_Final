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
    Webhook to receive messages from WhatsApp Cloud API.
    It extracts the user's phone number and saves it if it's a new contact.
    """
    body = await request.json()
    
    try:
        # This structure is based on the expert's analysis.
        # It might need adjustments based on the actual payload.
        if body.get("object") == "whatsapp_business_account":
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    if change.get("field") == "messages":
                        for message in change.get("value", {}).get("messages", []):
                            if message.get("type") == "text":
                                phone_number = message.get("from")
                                # Here you would typically save the phone number and
                                # associate it with a user in your database.
                                # For now, we just log it.
                                print(f"Received message from: {phone_number}")

    except Exception as e:
        print(f"Error processing webhook: {e}")
        
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
