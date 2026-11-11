
from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import check_database_connection
from app.api.routes.analytics import router as analytics_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="EventFlow API",
    description="Event Ticketing and Financial Analytics Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Welcome to EventFlow API",
        "status": "running"
    }


@app.get("/health/database")
def database_health():
    try:
        check_database_connection()

        return {
            "status": "healthy",
            "database": "connected"
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed."
        )


app.include_router(
    analytics_router,
    prefix="/api/analytics",
    tags=["Analytics"]
)
