import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Date,
    ForeignKey,
    VARBINARY,
    Boolean,
    Integer, # Added Integer for CantidadAcompanantes
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER

Base = declarative_base()

class Persona(Base):
    __tablename__ = 'Persona'
    __table_args__ = {'schema': 'terraqr'}

    PersonaId = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    QRToken = Column(UNIQUEIDENTIFIER, unique=True, nullable=False, default=uuid.uuid4)
    CURPHash = Column(VARBINARY(32), unique=True, nullable=True) # Made nullable
    Nombre = Column(String(150), nullable=False)
    ApellidoPaterno = Column(String(100), nullable=False)
    ApellidoMaterno = Column(String(100), nullable=False)
    FechaNacimiento = Column(Date, nullable=False)
    Genero = Column(String(30), nullable=False)
    Colonia = Column(String(150), nullable=False)
    Correo = Column(String(200), nullable=False)
    Telefono = Column(String(20), nullable=False)
    FechaRegistro = Column(DateTime, nullable=False, default=datetime.utcnow)
    TipoPersona = Column(String(30), nullable=False, default='Adulto') # New field
    AdultoResponsableId = Column(UNIQUEIDENTIFIER, ForeignKey('terraqr.Persona.PersonaId'), nullable=True) # New field
    CodigoPostal = Column(String(10), nullable=True) # New field

    asistencias = relationship("Asistencia", back_populates="persona")
    acompanantes = relationship("Persona", backref="adulto_responsable", remote_side=[PersonaId]) # New relationship for companions

class Operador(Base):
    __tablename__ = 'Operador'
    __table_args__ = {'schema': 'terraqr'}

    OperadorId = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    Nombre = Column(String(150), nullable=False)
    Usuario = Column(String(100), unique=True, nullable=False)
    ContrasenaHash = Column(String(255), nullable=False)
    Activo = Column(Boolean, nullable=False, default=True)
    FechaRegistro = Column(DateTime, nullable=False, default=datetime.utcnow)

class Evento(Base):
    __tablename__ = 'Evento'
    __table_args__ = {'schema': 'terraqr'}

    EventoId = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    EventoKey = Column(String(50), unique=True, nullable=False)
    NombreEvento = Column(String(200), nullable=False)
    Fecha = Column(DateTime, nullable=False)

    asistencias = relationship("Asistencia", back_populates="evento")

class Asistencia(Base):
    __tablename__ = 'Asistencia'
    __table_args__ = {'schema': 'terraqr'}

    AsistenciaId = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    PersonaId = Column(UNIQUEIDENTIFIER, ForeignKey('terraqr.Persona.PersonaId'), nullable=False)
    EventoId = Column(UNIQUEIDENTIFIER, ForeignKey('terraqr.Evento.EventoId'), nullable=False)
    FechaCheckIn = Column(DateTime, nullable=False, default=datetime.utcnow)
    CantidadAcompanantes = Column(Integer, nullable=True) # New field

    persona = relationship("Persona", back_populates="asistencias")
    evento = relationship("Evento", back_populates="asistencias")
