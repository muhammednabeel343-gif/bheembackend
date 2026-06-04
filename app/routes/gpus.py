from app.schemas.gpu import GPUCreate, GPUResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.gpu import GPU
from app.authentication.admin_jwt import get_current_admin

router = APIRouter(
    prefix="/admin/gpus",
    tags=["GPU Management"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("", response_model=list[GPUResponse])
def get_gpus(db: Session = Depends(get_db)):
    return db.query(GPU).all()


@router.get("/{gpu_id}", response_model=GPUResponse)
def get_gpu(gpu_id: int, db: Session = Depends(get_db)):
    gpu = db.query(GPU).filter(GPU.id == gpu_id).first()
    if not gpu:
        raise HTTPException(status_code=404, detail="GPU not found")
    return gpu


@router.post("", response_model=GPUResponse)
def create_gpu(
    gpu: GPUCreate,
    db: Session = Depends(get_db)
):
    existing_gpu = (
        db.query(GPU)
        .filter(GPU.name == gpu.name)
        .first()
    )

    if existing_gpu:
        raise HTTPException(
            status_code=400,
            detail="GPU already exists"
        )

    new_gpu = GPU(name=gpu.name)
    db.add(new_gpu)
    db.commit()
    db.refresh(new_gpu)

    return new_gpu


@router.put("/{gpu_id}", response_model=GPUResponse)
def update_gpu(
    gpu_id: int,
    gpu: GPUCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(GPU).filter(GPU.id == gpu_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="GPU not found")

    duplicate = db.query(GPU).filter(GPU.name == gpu.name, GPU.id != gpu_id).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="GPU name already exists")

    existing.name = gpu.name
    db.commit()
    db.refresh(existing)
    return existing


@router.delete("/{gpu_id}")
def delete_gpu(gpu_id: int, db: Session = Depends(get_db)):
    gpu = db.query(GPU).filter(GPU.id == gpu_id).first()
    if not gpu:
        raise HTTPException(status_code=404, detail="GPU not found")
    db.delete(gpu)
    db.commit()
    return {"message": "GPU deleted"}