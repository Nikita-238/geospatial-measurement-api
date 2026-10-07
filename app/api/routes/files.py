import os
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import File as FileModel


router = APIRouter(
    prefix="/api/files",
    tags=["Files"]
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".kml", ".zip"}


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
    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only .kml and .zip files are allowed."
        )

    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_type = extension.lstrip(".")

    db_file = FileModel(
        filename=file.filename,
        file_type=file_type,
        status="uploaded"
    )

    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return {
        "id": db_file.id,
        "filename": db_file.filename,
        "file_type": db_file.file_type,
        "status": db_file.status
    }
    
@router.get("/{file_id}/")

def get_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    db_file = db.get(FileModel, file_id)

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