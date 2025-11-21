from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.db import models

async def get_dashboard_stats(db: AsyncSession):
    """
    Calculates and returns the main statistics for the dashboard.
    """
    
    # Total registrations
    total_registrations = await db.scalar(select(func.count(models.Persona.PersonaId)))
    
    # Registrations by type
    registrations_by_type = await db.execute(
        select(models.Persona.TipoPersona, func.count(models.Persona.PersonaId))
        .group_by(models.Persona.TipoPersona)
    )
    registrations_by_type = {row[0]: row[1] for row in registrations_by_type}
    
    # Total attendance
    total_attendance = await db.scalar(select(func.count(models.Asistencia.AsistenciaId)))
    
    # Attendance by type
    attendance_by_type = await db.execute(
        select(models.Persona.TipoPersona, func.count(models.Asistencia.AsistenciaId))
        .join(models.Persona)
        .group_by(models.Persona.TipoPersona)
    )
    attendance_by_type = {row[0]: row[1] for row in attendance_by_type}
    
    # Attendance over time (last 24 hours)
    from datetime import datetime, timedelta
    attendance_over_time = await db.execute(
        select(func.cast(models.Asistencia.FechaCheckIn, func.Date()), func.count(models.Asistencia.AsistenciaId))
        .where(models.Asistencia.FechaCheckIn >= datetime.utcnow() - timedelta(days=1))
        .group_by(func.cast(models.Asistencia.FechaCheckIn, func.Date()))
        .order_by(func.cast(models.Asistencia.FechaCheckIn, func.Date()))
    )
    attendance_over_time = {row[0].strftime("%Y-%m-%d"): row[1] for row in attendance_over_time}

    return {
        "total_registrations": total_registrations,
        "registrations_by_type": registrations_by_type,
        "total_attendance": total_attendance,
        "attendance_by_type": attendance_by_type,
        "attendance_over_time": attendance_over_time,
    }
