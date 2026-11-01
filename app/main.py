from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import init_db, engine
from app.routers import students, ai

STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_HTML = STATIC_DIR / "index.html"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure SQLite database tables exist
    init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "A robust Python backend to manage student records using CRUD operations with "
        "FastAPI and SQLite. Includes an optional Ollama AI extension to answer natural-language "
        "questions grounded on database records.\n\n"
        "Built for the **EWB Edu Tech Pvt. Ltd. Internship Assignment**."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for local testing & web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory for CSS/JS assets if needed
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include REST Routers directly (e.g. /students, /ai/ask)
app.include_router(students.router)
app.include_router(ai.router)

# Also mount under /api/v1 for standard REST API versioning
app.include_router(students.router, prefix=settings.API_V1_STR)
app.include_router(ai.router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Web Interface"])
def home(request: Request):
    """
    Serves the live interactive Web Dashboard if requested via browser,
    or returns API metadata if requested with JSON accept header.
    """
    accept = request.headers.get("accept", "")
    if "text/html" in accept and INDEX_HTML.exists():
        return FileResponse(INDEX_HTML)
    
    # Return JSON API details for programmatic clients
    return {
        "project": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "company": "EWB Edu Tech Pvt. Ltd.",
        "status": "online",
        "documentation": "/docs",
        "redoc": "/redoc",
        "web_dashboard": "/",
        "endpoints": {
            "students_crud": "/students",
            "students_crud_v1": f"{settings.API_V1_STR}/students",
            "ai_query": "/ai/ask",
            "ai_query_v1": f"{settings.API_V1_STR}/ai/ask",
            "health_check": "/health",
        }
    }

@app.get("/dashboard", tags=["Web Interface"])
def dashboard():
    """Direct URL for the web dashboard."""
    if INDEX_HTML.exists():
        return FileResponse(INDEX_HTML)
    return HTMLResponse("<h1>Web Dashboard coming soon</h1>")

@app.get("/health", tags=["General"])
def health_check():
    # Verify database connection
    db_status = "healthy"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "ollama_configured_model": settings.OLLAMA_MODEL,
        "ollama_base_url": settings.OLLAMA_BASE_URL,
    }
