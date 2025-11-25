from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services import dashboard_service
from app.core.security import get_current_operador_from_cookie
from app.db import models

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats_api(
    request: Request, # Request object is needed for the cookie dependency
    db: AsyncSession = Depends(get_db),
    current_operador: models.Operador = Depends(get_current_operador_from_cookie)
):
    """
    Retrieves the main statistics for the dashboard. Requires operator authentication via cookie.
    """
    stats = await dashboard_service.get_dashboard_stats(db)
    return stats
