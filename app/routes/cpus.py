from app.schemas.cpu import CPUCreate, CPUResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cpu import CPU
from app.authentication.admin_jwt import get_current_admin

router = APIRouter(
    prefix="/admin/cpus",
    tags=["CPU Management"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("", response_model=list[CPUResponse])
def get_cpus(db: Session = Depends(get_db)):
    return db.query(CPU).all()


@router.get("/{cpu_id}", response_model=CPUResponse)
def get_cpu(cpu_id: int, db: Session = Depends(get_db)):
    cpu = db.query(CPU).filter(CPU.id == cpu_id).first()
    if not cpu:
        raise HTTPException(status_code=404, detail="CPU not found")
    return cpu


@router.post("", response_model=CPUResponse)
def create_cpu(
    cpu: CPUCreate,
    db: Session = Depends(get_db)
):
    existing_cpu = (
        db.query(CPU)
        .filter(CPU.name == cpu.name)
        .first()
    )

    if existing_cpu:
        raise HTTPException(
            status_code=400,
            detail="CPU already exists"
        )

    new_cpu = CPU(name=cpu.name)
    db.add(new_cpu)
    db.commit()
    db.refresh(new_cpu)

    return new_cpu


@router.put("/{cpu_id}", response_model=CPUResponse)
def update_cpu(
    cpu_id: int,
    cpu: CPUCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(CPU).filter(CPU.id == cpu_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="CPU not found")

    duplicate = db.query(CPU).filter(CPU.name == cpu.name, CPU.id != cpu_id).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="CPU name already exists")

    existing.name = cpu.name
    db.commit()
    db.refresh(existing)
    return existing


@router.delete("/{cpu_id}")
def delete_cpu(cpu_id: int, db: Session = Depends(get_db)):
    cpu = db.query(CPU).filter(CPU.id == cpu_id).first()
    if not cpu:
        raise HTTPException(status_code=404, detail="CPU not found")
    db.delete(cpu)
    db.commit()
    return {"message": "CPU deleted"}