from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select # Added select
from uuid import UUID # Added UUID
from typing import Optional # Added Optional

from app.db import models, schemas
from app.db.database import get_db
from app.services import (
    operadores_service,
    personas_service,
    eventos_service,
    accesos_service,
)
from app.core.security import create_access_token
from app.core.config import settings
from jose import JWTError, jwt

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


async def get_current_operador_from_cookie(
    request: Request, db: AsyncSession = Depends(get_db)
) -> Optional[models.Operador]:
    """Tries to authenticate an operator from a cookie."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        operador_id: str = payload.get("sub")
        if operador_id is None:
            return None
        return await operadores_service.get_operador_by_id(db, operador_id=operador_id)
    except JWTError:
        return None


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    """Displays the login page."""
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": error}
    )


@router.post("/login")
async def handle_login(
    request: Request,
    db: AsyncSession = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
):
    """Handles login form submission, sets cookie, and redirects."""
    operador = await operadores_service.authenticate_operador(
        db, usuario=username, contrasena=password
    )
    if not operador:
        return await login_page(request, error="Usuario o contraseña no válidos.")

    access_token = create_access_token(data={"sub": str(operador.OperadorId)})
    
    # Redirect to the validation page if 'next' is in query params
    next_url = request.query_params.get("next", "/scan") # Changed default redirect
    response = RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token", value=access_token, httpy_only=True, samesite="Lax"
    )
    return response

@router.post("/logout")
async def logout(request: Request):
    """Logs out the user by clearing the cookie."""
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response


@router.get("/scan", response_class=HTMLResponse) # Changed from /web/panel
async def scan_page(
    request: Request,
    current_operador: models.Operador = Depends(get_current_operador_from_cookie),
    message: Optional[str] = None,
    error: Optional[str] = None,
):
    """A simple scan page for operators to input a QR token."""
    if not current_operador:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse("scan_input.html", {
        "request": request, 
        "current_operador": current_operador,
        "message": message,
        "error": error
    })


@router.get("/scan/{qr_token}", response_class=HTMLResponse)
async def validate_and_register_qr_page( # Renamed function
    request: Request,
    qr_token: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Validates a citizen's QR code and automatically registers access.
    """
    current_operador = await get_current_operador_from_cookie(request, db)
    if not current_operador:
        return RedirectResponse(
            url=f"/login?next=/scan/{qr_token}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    persona = await personas_service.get_persona_by_qr_token(db, qr_token)
    if not persona:
        return templates.TemplateResponse(
            "qr_validate.html",
            {
                "request": request,
                "current_operador": current_operador,
                "validation_status": "invalid", # New status
                "error": "El código QR no es válido o no corresponde a ningún ciudadano registrado.",
            },
        )

    # Attempt to register access automatically
    validation_status = "success"
    message = "Acceso registrado correctamente."
    error = None
    
    # Get the number of companions for this persona
    # This assumes the adult's QR is scanned.
    # We need to count how many companions are linked to this adult.
    num_companions = 0
    if persona.TipoPersona == "Adulto":
        # Fetch companions linked to this adult
        companions_result = await db.execute(
            select(models.Persona).filter(models.Persona.AdultoResponsableId == persona.PersonaId)
        )
        num_companions = len(companions_result.scalars().all())

    try:
        # Use the fixed EventoKeyActual from the ASP.NET spec
        await accesos_service.register_asistencia(db, qr_token, "concierto2025", cantidad_acompanantes=num_companions)
    except ValueError as e:
        validation_status = "already_registered" if "ya tiene registrada" in str(e) else "error"
        error = str(e)
        message = None # Clear message if there's an error

    # For this version, we assume a single event for check-in, like "concierto2025"
    evento_concierto = await eventos_service.get_evento_by_key(db, "concierto2025")
    
    validation_data = schemas.WebValidationResult(
        persona=schemas.PersonaPublic(
            NombreCompleto=f"{persona.Nombre} {persona.ApellidoPaterno} {persona.ApellidoMaterno}",
            Colonia=persona.Colonia,
            CodigoPostal=persona.CodigoPostal, # New field
            FechaNacimiento=persona.FechaNacimiento,
            Genero=persona.Genero,
            TipoPersona=persona.TipoPersona,
            CantidadAcompanantesRegistrados=num_companions
        ),
        eventos_disponibles=[evento_concierto] if evento_concierto else [],
        mensaje=message,
        error=error,
        cantidad_acompanantes_registrados=num_companions
    )

    return templates.TemplateResponse(
        "qr_validate.html",
        {
            "request": request,
            "current_operador": current_operador,
            "validation_data": validation_data,
            "persona_id": persona.PersonaId,
            "qr_token": qr_token,
            "validation_status": validation_status, # Pass status to template
        },
    )

# The POST /access/{qr_token} endpoint is no longer needed as registration is automatic on GET
# @router.post("/access/{qr_token}")
# async def handle_web_access(...):
#     pass

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    current_operador: models.Operador = Depends(get_current_operador_from_cookie),
):
    """Displays the dashboard page."""
    if not current_operador:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse("dashboard.html", {"request": request, "current_operador": current_operador})