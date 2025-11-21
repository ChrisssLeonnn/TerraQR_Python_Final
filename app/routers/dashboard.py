from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services import dashboard_service
from app.core.security import get_current_operador
from app.db import models

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats_api(
    db: AsyncSession = Depends(get_db),
    current_operador: models.Operador = Depends(get_current_operador)
):
    """
    Retrieves the main statistics for the dashboard. Requires operator authentication.
    """
    stats = await dashboard_service.get_dashboard_stats(db)
    return stats
