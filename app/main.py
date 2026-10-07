from fastapi import FastAPI

from app.api.routes.files import router as files_router


app = FastAPI(
    title="Geospatial File Measurement API",
    description="Backend API for processing geospatial files and calculating measurements.",
    version="1.0.0"
)


app.include_router(files_router)


@app.get("/")
def root():
    return {
        "message": "Geospatial File Measurement API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }