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
    Integer, 
    UUID,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Persona(Base):
    __tablename__ = 'Persona'

    PersonaId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    QRToken = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    Nombre = Column(String(150), nullable=False)
    ApellidoPaterno = Column(String(100), nullable=False)
    ApellidoMaterno = Column(String(100), nullable=False)
    AnioNacimiento = Column(Integer, nullable=False)
    Genero = Column(String(30), nullable=False)
    Colonia = Column(String(150), nullable=False)
    Correo = Column(String(200), nullable=False)
    Telefono = Column(String(20), nullable=False)
    FechaRegistro = Column(DateTime, nullable=False, default=datetime.utcnow)
    TipoPersona = Column(String(30), nullable=False)
    CodigoPostal = Column(String(10), nullable=True)

    asistencias = relationship("Asistencia", back_populates="persona")

class Operador(Base):
    __tablename__ = 'Operador'

    OperadorId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    Nombre = Column(String(150), nullable=False)
    Usuario = Column(String(100), unique=True, nullable=False)
    ContrasenaHash = Column(String(255), nullable=False)
    Activo = Column(Boolean, nullable=False, default=True)
    FechaRegistro = Column(DateTime, nullable=False, default=datetime.utcnow)

class Evento(Base):
    __tablename__ = 'Evento'

    EventoId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    EventoKey = Column(String(50), unique=True, nullable=False)
    NombreEvento = Column(String(200), nullable=False)
    Fecha = Column(DateTime, nullable=False)

    asistencias = relationship("Asistencia", back_populates="evento")

class Asistencia(Base):
    __tablename__ = 'Asistencia'

    AsistenciaId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    PersonaId = Column(UUID(as_uuid=True), ForeignKey('Persona.PersonaId'), nullable=False)
    EventoId = Column(UUID(as_uuid=True), ForeignKey('Evento.EventoId'), nullable=False)
    FechaCheckIn = Column(DateTime, nullable=False, default=datetime.utcnow)

    persona = relationship("Persona", back_populates="asistencias")
    evento = relationship("Evento", back_populates="asistencias")
