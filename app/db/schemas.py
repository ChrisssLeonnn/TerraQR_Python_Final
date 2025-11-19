from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime

# --- Base Schemas ---

class PersonaBase(BaseModel):
    Nombre: str = Field(..., max_length=150)
    ApellidoPaterno: str = Field(..., max_length=100)
    ApellidoMaterno: str = Field(..., max_length=100)
    FechaNacimiento: date
    Genero: str = Field(..., max_length=30)
    Colonia: str = Field(..., max_length=150)
    Correo: EmailStr = Field(..., max_length=200)
    Telefono: str = Field(..., max_length=20)
    CodigoPostal: Optional[str] = Field(None, max_length=10) # New field

class PersonaCreate(PersonaBase):
    CURP: Optional[str] = Field(None, min_length=18, max_length=18) # Made optional
    TipoPersona: str = Field("Adulto", max_length=30) # New field

class Persona(PersonaBase):
    PersonaId: UUID
    QRToken: UUID
    FechaRegistro: datetime
    TipoPersona: str # New field
    AdultoResponsableId: Optional[UUID] = None # New field

    class Config:
        from_attributes = True

class PersonaWithQR(Persona):
    qr_url: str

class PersonaPublic(BaseModel):
    NombreCompleto: str
    Colonia: str
    CodigoPostal: Optional[str] = None # New field
    FechaNacimiento: date
    Genero: str
    TipoPersona: str # New field
    CantidadAcompanantesRegistrados: Optional[int] = None # For display on QR validation page

    class Config:
        from_attributes = True


class OperadorBase(BaseModel):
    Nombre: str = Field(..., max_length=150)
    Usuario: str = Field(..., max_length=100)

class OperadorCreate(OperadorBase):
    password: str

class Operador(OperadorBase):
    OperadorId: UUID
    Activo: bool
    FechaRegistro: datetime

    class Config:
        from_attributes = True


class EventoBase(BaseModel):
    EventoKey: str = Field(..., max_length=50)
    NombreEvento: str = Field(..., max_length=200)
    Fecha: datetime

class EventoCreate(EventoBase):
    pass

class Evento(EventoBase):
    EventoId: UUID
    FechaRegistro: datetime

    class Config:
        from_attributes = True


# --- Token Schemas ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: Optional[str] = None


# --- API Request Body Schemas ---

class CheckInRequest(BaseModel):
    qr_token: UUID
    evento_key: str

# New DTOs for group registration
class AcompananteCreate(BaseModel):
    Nombre: str = Field(..., max_length=150)
    ApellidoPaterno: str = Field(..., max_length=100)
    ApellidoMaterno: str = Field(..., max_length=100)
    FechaNacimiento: date
    Genero: str = Field(..., max_length=30)
    TipoPersona: str = Field(..., max_length=30, pattern="^(TerceraEdad|Nino)$") # Must be TerceraEdad or Nino
    CodigoPostal: Optional[str] = Field(None, max_length=10) # New field

class GroupRegistrationRequest(BaseModel):
    adulto: PersonaCreate
    acompanantes: Optional[List[AcompananteCreate]] = None


# --- Web Validation Schemas ---
class WebValidationResult(BaseModel):
    persona: PersonaPublic
    eventos_disponibles: List[Evento]
    mensaje: Optional[str] = None
    error: Optional[str] = None
    cantidad_acompanantes_registrados: Optional[int] = None # For display on QR validation page
    cantidad_acompanantes_confirmados: Optional[int] = None # For operator input

# New DTO for WhatsApp delivery response
class WhatsAppQRResponse(BaseModel):
    status: str
    message: str
    qr_url: str
    phone_number: str
    persona_id: UUID
    qr_token: UUID
