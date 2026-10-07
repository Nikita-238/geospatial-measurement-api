import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import (
    File as FileModel,
    Measurement,
)
from app.services.geospatial_service import (
    calculate_measurements,
    read_geospatial_file,
)


router = APIRouter(
    prefix="/api/files",
    tags=["Files"]
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".kml", ".zip"}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
CHUNK_SIZE = 1024 * 1024  # 1 MB


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/")
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only .kml and .zip files are allowed."
        )

    safe_filename = f"{uuid.uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / safe_filename

    # ---------------------------------------------------------
    # Step 1: Save uploaded file with size protection
    # ---------------------------------------------------------
    total_size = 0
    file_too_large = False

    try:
        with file_path.open("wb") as buffer:
            while True:
                chunk = file.file.read(CHUNK_SIZE)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    file_too_large = True
                    break

                buffer.write(chunk)

    except OSError:
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Unable to save the uploaded file."
        )

    if file_too_large:
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=413,
            detail="File size exceeds the 10 MB limit."
        )

    # ---------------------------------------------------------
    # Step 2: Create database record
    # ---------------------------------------------------------
    try:
        file_type = extension.lstrip(".")

        db_file = FileModel(
            filename=file.filename,
            file_type=file_type,
            status="uploaded"
        )

        db.add(db_file)
        db.commit()
        db.refresh(db_file)

    except Exception:
        db.rollback()
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Unable to save file information."
        )

    # ---------------------------------------------------------
    # Step 3: Process geospatial file
    # ---------------------------------------------------------
    try:
        gdf = read_geospatial_file(file_path)

        measurement_results = calculate_measurements(gdf)

        db_file.crs = (
            gdf.crs.to_string()
            if gdf.crs
            else None
        )

        db_file.feature_count = len(gdf)

        for result in measurement_results:
            measurement = Measurement(
                file_id=db_file.id,
                feature_id=result["feature_id"],
                geometry_type=result["geometry_type"],
                area=result["area"],
                length=result["length"],
                measurement_unit=result["measurement_unit"],
                status=result["status"]
            )

            db.add(measurement)

        db_file.status = "processed"

        db.commit()
        db.refresh(db_file)

        # Uploaded file is no longer required.
        file_path.unlink(missing_ok=True)

    except ValueError as error:
        db.rollback()

        db_file = db.get(
            FileModel,
            db_file.id
        )

        if db_file:
            db_file.status = "failed"
            db.commit()

        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        db.rollback()

        db_file = db.get(
            FileModel,
            db_file.id
        )

        if db_file:
            db_file.status = "failed"
            db.commit()

        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail=(
                "An unexpected error occurred "
                "while processing the file."
            )
        )

    return {
        "id": db_file.id,
        "filename": db_file.filename,
        "file_type": db_file.file_type,
        "crs": db_file.crs,
        "feature_count": db_file.feature_count,
        "status": db_file.status
    }


@router.get("/{file_id}/")
def get_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    db_file = db.get(
        FileModel,
        file_id
    )

    if db_file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    return {
        "id": db_file.id,
        "filename": db_file.filename,
        "file_type": db_file.file_type,
        "crs": db_file.crs,
        "feature_count": db_file.feature_count,
        "status": db_file.status,
        "created_at": db_file.created_at,
    }


@router.get("/{file_id}/measurements/")
def get_measurements(
    file_id: int,
    db: Session = Depends(get_db)
):
    db_file = db.get(
        FileModel,
        file_id
    )

    if db_file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    measurements = (
        db.query(Measurement)
        .filter(
            Measurement.file_id == file_id
        )
        .all()
    )

    return [
        {
            "feature_id": measurement.feature_id,
            "geometry_type": measurement.geometry_type,
            "area": measurement.area,
            "length": measurement.length,
            "measurement_unit": measurement.measurement_unit,
            "status": measurement.status
        }
        for measurement in measurements
    ]