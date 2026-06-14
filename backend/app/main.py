"""FastAPI application factory."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.exceptions import register_exception_handlers
from app.routers import accidents, aggregates, health, indicators, metadata, regions, time

def create_app() -> FastAPI:
    """Create and configure the API application."""
    application = FastAPI(title="UnfallAtlas API", description="German road accident open data integration service", version="1.0.0", docs_url="/docs", redoc_url="/redoc", openapi_url="/openapi.json", license_info={"name": "Datenlizenz Deutschland – Namensnennung – Version 2.0", "url": "https://www.govdata.de/dl-de/by-2-0"})
    application.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
    application.add_middleware(GZipMiddleware, minimum_size=1000)
    register_exception_handlers(application)
    application.include_router(health.router, tags=["Health"])
    application.include_router(regions.router, prefix="/regions", tags=["Regions"])
    application.include_router(accidents.router, prefix="/accidents", tags=["Accidents"])
    application.include_router(aggregates.router, prefix="/aggregates", tags=["Aggregates"])
    application.include_router(time.router, prefix="/time", tags=["Time"])
    application.include_router(indicators.router, prefix="/indicators", tags=["Indicators"])
    application.include_router(metadata.router, prefix="/metadata", tags=["Metadata"])

    @application.get("/", summary="API index", description="Returns links to the API documentation and health endpoint.")
    async def index() -> dict[str, str]:
        """Return basic API navigation links."""
        return {
            "name": "UnfallAtlas API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
        }

    return application
app = create_app()
