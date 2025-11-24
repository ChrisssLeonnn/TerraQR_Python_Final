from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime

# --- Base Schemas ---

class PersonaBase(BaseModel):
    Nombre: Optional[str] = Field(None, max_length=150)
    ApellidoPaterno: Optional[str] = Field(None, max_length=100)
    ApellidoMaterno: Optional[str] = Field(None, max_length=100)
    AnioNacimiento: Optional[int] = None
    Genero: Optional[str] = Field(None, max_length=30)
    Colonia: Optional[str] = Field(None, max_length=150)
    Correo: Optional[EmailStr] = Field(None, max_length=200)
    Telefono: Optional[str] = Field(None, max_length=20)
    CodigoPostal: Optional[str] = Field(None, max_length=10) # New field

class PersonaCreate(PersonaBase):
    pass

class Persona(PersonaBase):
    PersonaId: UUID
    QRToken: UUID
    FechaRegistro: datetime
    TipoPersona: str

    class Config:
        from_attributes = True

class PersonaWithPDF(Persona):
    pdf_url: str

class PersonaPublic(BaseModel):
    NombreCompleto: str
    Colonia: str
    CodigoPostal: Optional[str] = None
    AnioNacimiento: int
    Genero: str
    TipoPersona: str

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

# --- Web Validation Schemas ---
class WebValidationResult(BaseModel):
    persona: PersonaPublic
    eventos_disponibles: List[Evento]
    mensaje: Optional[str] = None
    error: Optional[str] = None
