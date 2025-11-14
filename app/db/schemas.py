from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime

# --- Base Schemas ---

class PersonaBase(BaseModel):
    Nombre: str = Field(..., max_length=150) # Changed from 120 to 150
    ApellidoPaterno: str = Field(..., max_length=100)
    ApellidoMaterno: str = Field(..., max_length=100)
    FechaNacimiento: date
    Genero: str = Field(..., max_length=30)
    Colonia: str = Field(..., max_length=150)
    Correo: EmailStr = Field(..., max_length=200) # Changed from 150 to 200
    Telefono: str = Field(..., max_length=20)

class PersonaCreate(PersonaBase):
    CURP: str = Field(..., min_length=18, max_length=18)

class Persona(PersonaBase):
    PersonaId: UUID
    QRToken: UUID
    FechaRegistro: datetime

    class Config:
        from_attributes = True

class PersonaWithQR(Persona):
    qr_url: str

class PersonaPublic(BaseModel):
    NombreCompleto: str
    Colonia: str
    FechaNacimiento: date
    Genero: str

    class Config:
        from_attributes = True


class OperadorBase(BaseModel):
    Nombre: str = Field(..., max_length=150) # Changed from 120 to 150
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
    EventoKey: str = Field(..., max_length=50) # New field
    NombreEvento: str = Field(..., max_length=200)
    Fecha: datetime
    # Ubicacion and Activo fields removed

class EventoCreate(EventoBase):
    pass

class Evento(EventoBase):
    EventoId: UUID
    # FechaRegistro: datetime # Removed as per new schema
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
    evento_key: str # Changed from evento_id to evento_key

# --- Web Validation Schemas ---
class WebValidationResult(BaseModel):
    persona: PersonaPublic
    eventos_disponibles: List[Evento] # Changed from eventos_activos
    mensaje: Optional[str] = None
    error: Optional[str] = None
