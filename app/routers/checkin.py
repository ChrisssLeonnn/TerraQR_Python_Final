from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import schemas, models
from app.db.database import get_db
from app.services import accesos_service
from app.core.security import get_current_operador

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_asistencia_api(
    request: schemas.CheckInRequest,
    db: AsyncSession = Depends(get_db),
    current_operador: models.Operador = Depends(get_current_operador)
):
    """
    Registers a person's attendance to an event. Requires operator authentication.
    """
    try:
        asistencia = await accesos_service.register_asistencia(
            db=db,
            qr_token=request.qr_token,
            evento_key=request.evento_key,
        )
        return {"status": "success", "detail": "Asistencia registrada correctamente.", "asistencia_id": asistencia.AsistenciaId}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        # Log exception e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ocurrió un error al registrar la asistencia.")
