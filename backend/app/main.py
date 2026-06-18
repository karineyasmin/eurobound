from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from app.core.logger import logger
from app.api import spatial_router
from app.api import user_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages the startup and shutdown lifecycles of the application"""

    logger.info("🚀 EuroBound Spatial API is starting up...")
    logger.info("PostGIS database pool connection initialized successfully.")

    yield

    logger.warning("EuroBound Spatial API is shutting down...")


app = FastAPI(
    title="EuroBound API",
    description="Geotech Spatial API for European Relocation and Route Planning",
    version="0.1.0",
    lifespan=lifespan,
)

origins = [
    "http://localhost:8501",  # Default Streamlit port
    "http://127.0.0.1:8501",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Allows all HTTP headers
)
app.include_router(user_router)
app.include_router(spatial_router)


@app.get("/", tags=["Health"], response_model=dict[str, str])
async def read_root() -> dict[str, str]:
    """Performs a basic applicaiton health check"""
    logger.debug("Health check endpoint triggered.")
    return {
        "status": "healthy",
        "application": "EuroBound API",
        "spatial_engine": "PostGIS 3.4 Enabled",
    }
