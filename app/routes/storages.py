from app.schemas.storage import StorageCreate, StorageResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.storage import Storage
from app.authentication.admin_jwt import get_current_admin

router = APIRouter(
    prefix="/admin/storages",
    tags=["Storage Management"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("", response_model=list[StorageResponse])
def get_storages(db: Session = Depends(get_db)):
    return db.query(Storage).all()


@router.get("/{storage_id}", response_model=StorageResponse)
def get_storage(storage_id: int, db: Session = Depends(get_db)):
    storage = db.query(Storage).filter(Storage.id == storage_id).first()
    if not storage:
        raise HTTPException(status_code=404, detail="Storage not found")
    return storage


@router.post("", response_model=StorageResponse)
def create_storage(
    storage: StorageCreate,
    db: Session = Depends(get_db)
):
    existing_storage = (
        db.query(Storage)
        .filter(Storage.size == storage.size)
        .first()
    )

    if existing_storage:
        raise HTTPException(
            status_code=400,
            detail="Storage size already exists"
        )

    new_storage = Storage(size=storage.size)
    db.add(new_storage)
    db.commit()
    db.refresh(new_storage)

    return new_storage


@router.put("/{storage_id}", response_model=StorageResponse)
def update_storage(
    storage_id: int,
    storage: StorageCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Storage).filter(Storage.id == storage_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Storage not found")

    duplicate = db.query(Storage).filter(Storage.size == storage.size, Storage.id != storage_id).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="Storage size already exists")

    existing.size = storage.size
    db.commit()
    db.refresh(existing)
    return existing


@router.delete("/{storage_id}")
def delete_storage(storage_id: int, db: Session = Depends(get_db)):
    storage = db.query(Storage).filter(Storage.id == storage_id).first()
    if not storage:
        raise HTTPException(status_code=404, detail="Storage not found")
    db.delete(storage)
    db.commit()
    return {"message": "Storage deleted"}