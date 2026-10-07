from fastapi import FastAPI

app = FastAPI(
    title="Geospatial File Measurement API",
    description="Backend API for processing geospatial files and calculating measurements.",
    version="1.0.0"
)


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