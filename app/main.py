from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.routers import auth, personas, eventos, checkin, web
from app.db.database import engine

app = FastAPI(
    title="TerraQR Municipal System API (Final Version)",
    description="Backend oficial para el sistema de registro y control de acceso TerraQR, adaptado al esquema de BD del proyecto ASP.NET.",
    version="1.0.0"
)

# Mount static files (for CSS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# --- API Routers ---
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación API"])
app.include_router(personas.router, prefix="/api/personas", tags=["Personas API"])
app.include_router(eventos.router, prefix="/api/eventos", tags=["Eventos API"])
app.include_router(checkin.router, prefix="/api/checkin", tags=["Check-In API"])

# --- Web Interface Routers ---
# The user specified the QR URL should be terraqr.xyz/scan/{token}
# This means our web router needs to handle that exact path.
app.include_router(web.router, tags=["Interfaz Web Operador"])


@app.on_event("startup")
async def startup_event():
    # If you needed to create tables, you would do it here.
    # await create_tables()
    pass

@app.get("/", include_in_schema=False)
async def root(request: Request):
    """
    Redirects the root URL to the web login page.
    """
    # Check if user is already logged in via cookie
    token = request.cookies.get("access_token")
    if token:
        return RedirectResponse(url="/scan") # Redirect to the scan input page
    return RedirectResponse(url="/login")
